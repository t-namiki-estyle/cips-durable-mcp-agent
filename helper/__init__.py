"""
Finance Department用のカスタムMSGテキストエクストラクター
標準のMSGTextExtractorをオーバーライドし、財務部に特化したメール解析を行います。

TODO: 暫定的な処理のため、将来的にi-Style本体に取り込むことを検討しています。
"""

import io
import logging
import re
import base64
import os
from typing import List, Dict, Any, Callable, Optional, Union
import extract_msg
from i_style.text_extractor.base import BaseTextExtractor
from i_style.text_extractor import FileTextExtractor
from i_style.llm import ModelRegistry
from config import FILE_EXTENSIONS

# 添付ファイルとして文字起こしを行うファイルの拡張子のリスト
TRANSCRIBE_EXT = ["jpg", "jpeg", "png", "tiff", "tif", "pdf"]

class FinanceDepartmentMailParser(BaseTextExtractor):
    """
    財務部向けにカスタマイズされたMSGファイルの文字起こしクラス

    カスタマイズした点:
    - 埋め込み画像の文字起こしの追加
    - 添付ファイルは "transcribe_attachments" に拡張子を指定またはTrueを付与(全拡張子対応扱い)することにより文字起こしを実施
    """
    def __init__(
        self,
        extractor: Optional[Callable[[bytes, str], Any]] = None,
        transcribe_attachments: Union[bool, List[str]] = False
    ):
        """
        FinanceDepartmentMailParserの初期化
        Args:
            extractor: 添付ファイルを文字起こしするコールバック
            transcribe_attachments: 添付ファイルの文字起こしを行うかどうか。文字起こしを行うファイルの拡張子を指定することも可能
        """
        if extractor is None:
            raise ValueError(
                "extractor を渡してください（画像の文字起こしに必要です）"
            )
        self._extractor = extractor
        self._transcribe_attachments = transcribe_attachments

    def _safe_get_field(self, msg, field_name: str, default: str = "Unknown") -> str:
        """
        msgオブジェクトからフィールドを取得する

        Args:
            msg: extract_msgのMessageオブジェクト
            field_name: 取得するフィールド名
            default: デフォルト値

        Returns:
            フィールドの値（エラー時はデフォルト値）
        """
        try:
            value = getattr(msg, field_name, None)
            return value if value else default
        except (UnicodeDecodeError, Exception) as e:
            logging.warning(f"Failed to decode {field_name}: {e}")
            return f"{default} (decode error)"

    async def extract_text(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        msgファイルを受け取り、抽出したテキストとページ番号を返します。
        財務部用にフォーマットをカスタマイズしています。

        処理の流れ:
            1. extract_msgを使用してMSGファイルからメール情報（件名、本文、送信者、受信者、CC、日付）を抽出
            2. 埋め込み画像の文字起こしを実施
            3. 添付画像の文字起こしを実施

        Args:
            file_content (bytes): msgファイルのバイト列
        Returns:
            List[Dict[str, Any]]:
                メール本文を1ページ目とし、画像がある場合は2ページ目以降に格納します。
                {
                    "page_number": int, # ページ番号
                    "texts": str  # そのページの文字起こしテキスト
                }
        """
        msg = None
        try:
            msg = extract_msg.Message(io.BytesIO(file_content))
            self._msg = msg  # 埋め込み画像抽出用に保存

            # 各フィールドを安全に取得
            subject = self._safe_get_field(msg, "subject", "No Subject")
            sender = self._safe_get_field(msg, "sender", "Unknown Sender")
            to = self._safe_get_field(msg, "to", "Unknown Recipient")
            cc = self._safe_get_field(msg, "cc", "")
            body = self._safe_get_field(msg, "body", "No Body")

            # 財務部用のメールフォーマット
            email_parts = []
            # 件名
            email_parts.append(subject)
            # From
            email_parts.append("From")
            email_parts.append(sender)
            # To
            email_parts.append("To")
            email_parts.append(to)
            # CC（存在する場合のみ）
            if cc:
                email_parts.append("Cc")
                email_parts.append(cc)
            # Recipients（toとccから抽出したメールアドレス）
            recipients = []
            if to and to != "Unknown Recipient":
                to_addresses = self._extract_email_addresses(to)
                recipients.extend(to_addresses)
            if cc:
                cc_addresses = self._extract_email_addresses(cc)
                recipients.extend(cc_addresses)
            if recipients:
                email_parts.append("Recipients")
                email_parts.append("; ".join(recipients))
            # 本文
            if body:
                email_parts.append(body)
            # 全体を改行で結合
            email_text = "\n".join(email_parts)
            pages = [{"page_number": 1, "texts": email_text}]

            page_no = 2
            # 埋め込み画像の処理 (Base64)
            pages, page_no = await self._process_base64_images(msg, pages, page_no)

            # 添付ファイルの処理
            if getattr(msg, "attachments", None):
                for att in msg.attachments:
                    file_name = att.longFilename or att.shortFilename or "unknown"
                    file_name = file_name.rstrip("\x00").strip()
                    att_content = att.data
                    if not att_content:
                        logging.warning(f"Attachment data not found for {file_name}, skipped.")
                        continue
                    
                    att_ext = os.path.splitext(file_name)[1].lower().lstrip(".") or "unknown"

                    if (self._transcribe_attachments is True) or \
                        (isinstance(self._transcribe_attachments, list) and att_ext in self._transcribe_attachments):
                        try:
                            att_pages = await self._extractor(att_content, att_ext)
                        except Exception as e:
                            logging.error(f"Failed to transcribe attached image {file_name}: {e}")
                            att_pages = [{"texts": f"Attached File ({file_name}): [{file_name}]の文字起こしに失敗しました"}]

                        for p in att_pages:
                            # 添付ファイルか、CIDを持つ埋め込みファイルかどうかを判定 (CID: HTMLメールにファイルを埋め込むために使用される「Content-ID」の略)
                            content_id = getattr(att, "contentId", None) or getattr(att, "cid", None)
                            prefix = "Inline File" if content_id else "Attached File"
                            pages.append({
                                "page_number": page_no,
                                "texts": f"{prefix} ({file_name}):\n{p.get('texts','')}"
                            })
                            page_no += 1
            return pages
        except Exception as e:
            logging.error(f"Error extracting text from msg: {e}")
            raise RuntimeError(f"Error extracting text from msg: {e}")
        finally:
            if msg and hasattr(msg, "close"):
                try:
                    msg.close()
                except Exception:
                    logging.warning("Failed to close msg object.")
            self._msg = None  # クリーンアップ

    def _extract_base64_images(self, html_body: str) -> List[Dict[str, Any]]:
        """
        HTML本文からbase64エンコードされた画像を抽出する

        Args:
            html_body: HTML本文

        Returns:
            画像データのリスト。各要素は {"name": str, "content": bytes, "ext": str} の形式
        """
        images = []
        # base64エンコードされた画像を抽出 (data:image/...;base64,xxxxx の形式)
        base64_pattern = r'data:image/([^;]+);base64,([^"\']+)'
        for match in re.finditer(base64_pattern, html_body, re.IGNORECASE):
            img_type = match.group(1).lower()
            base64_data = match.group(2)
            try:
                img_content = base64.b64decode(base64_data)
                images.append({
                    "name": f"inline_base64.{img_type}",
                    "content": img_content,
                    "ext": img_type
                })
            except Exception as e:
                logging.warning(f"Failed to decode base64 image: {e}")
        return images

    def _extract_email_addresses(self, text: str) -> List[str]:
        """
        テキストからメールアドレスを抽出する

        Args:
            text: メールアドレスを含むテキスト

        Returns:
            抽出されたメールアドレスのリスト
        """
        # メールアドレスのパターン
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return emails
    
    async def _process_base64_images(self, msg, pages: List[Dict[str, Any]], page_no: int) -> tuple[List[Dict[str, Any]], int]:
        """
        メール本文内の埋め込み画像（Base64）を処理する

        Args: 
            msg: extract_msgのMessageオブジェクト
            pages: 現在のページリスト
            page_no: ページ番号
        
        Returns:
            tuple[List[Dict[str, Any]], int]:
                更新されたページリスト、次のページ番号
        """
        html_body = getattr(msg, "htmlBody", None)
        if not html_body:
            return pages, page_no

        if isinstance(html_body, bytes):
            try:
                html_body = html_body.decode('utf-8', errors='ignore')
            except Exception as e:
                logging.warning(f"Failed to decode HTML body: {e}")
                html_body = ""

        # Base64エンコードされた画像を処理
        base64_images = self._extract_base64_images(html_body)
        for img_data in base64_images:
            try:
                img_pages = await self._extractor(img_data["content"], img_data["ext"])
                for p in img_pages:
                    pages.append({
                        "page_number": page_no,
                        "texts": f"Inline Image (base64 {img_data['name']}):\n{p.get('texts','')}"
                    })
                    page_no += 1
            except Exception as e:
                logging.error(f"Failed to transcribe base64 image {img_data['name']}: {e}")
                pages.append({
                    "page_number": page_no,
                    "texts": f"Inline Image (base64 {img_data['name']}): [{img_data['name']}]の文字起こしに失敗しました"
                })
                page_no += 1
        return pages, page_no



# 財務部用のFileTextExtractorインスタンスを事前に初期化
FINANCE_DEPARTMENT_FILE_TEXT_EXTRACTOR = FileTextExtractor(
    file_extension_list=FILE_EXTENSIONS,
    model_registry=ModelRegistry(),
    msg_transcribe_attachments=False,
)

# MSGファイルの処理をFinanceDepartmentMailParserにオーバーライド
if "msg" in FINANCE_DEPARTMENT_FILE_TEXT_EXTRACTOR.selected_extractors:
    FINANCE_DEPARTMENT_FILE_TEXT_EXTRACTOR.selected_extractors["msg"]["instance"] = FinanceDepartmentMailParser(
        transcribe_attachments=TRANSCRIBE_EXT,
        extractor=FINANCE_DEPARTMENT_FILE_TEXT_EXTRACTOR.extract_text
    )
