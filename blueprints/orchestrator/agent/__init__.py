"""
各種エージェントの設定を読み込む
mode名をキーとしてservers, prompts, code_inputsを格納する
"""

# サンプル用のエージェントで使用するパラメーター
from blueprints.orchestrator.agent.default_config import MCP_SERVERS as DEFAULT_MCP_SERVERS
from blueprints.orchestrator.agent.default_config import PROMPTS as DEFAULT_PROMPTS
from blueprints.orchestrator.agent.default_config import MCP_CODE_INPUTS as DEFAULT_MCP_CODE_INPUTS

# 汎用
from blueprints.orchestrator.agent.genie_agent_config import MCP_SERVERS as GENIE_AGENT_MCP_SERVERS
from blueprints.orchestrator.agent.genie_agent_config import PROMPTS as GENIE_AGENT_PROMPTS
from blueprints.orchestrator.agent.genie_agent_config import MCP_CODE_INPUTS as GENIE_AGENT_MCP_CODE_INPUTS

# research用
from blueprints.orchestrator.agent.research_config import MCP_SERVERS as RESEARCH_MCP_SERVERS
from blueprints.orchestrator.agent.research_config import PROMPTS as RESEARCH_PROMPTS
from blueprints.orchestrator.agent.research_config import MCP_CODE_INPUTS as RESEARCH_MCP_CODE_INPUTS

# 監査予備調査:過去監査報告書分析エージェント用
from blueprints.orchestrator.agent.audit_precheck_config import MCP_SERVERS as AUDIT_PRECHECK_MCP_SERVERS
from blueprints.orchestrator.agent.audit_precheck_config import PROMPTS as AUDIT_PRECHECK_PROMPTS
from blueprints.orchestrator.agent.audit_precheck_config import MCP_CODE_INPUTS as AUDIT_PRECHECK_MCP_CODE_INPUTS

# 営業問い合わせ支援用
from blueprints.orchestrator.agent.panel_sales_enquiry_config import MCP_SERVERS as PANEL_SALES_ENQUIRY_MCP_SERVERS
from blueprints.orchestrator.agent.panel_sales_enquiry_config import PROMPTS as PANEL_SALES_ENQUIRY_PROMPTS
from blueprints.orchestrator.agent.panel_sales_enquiry_config import MCP_CODE_INPUTS as PANEL_SALES_ENQUIRY_MCP_CODE_INPUTS

# IRLエージェント用
from blueprints.orchestrator.agent.irl_config import MCP_SERVERS as IRL_MCP_SERVERS
from blueprints.orchestrator.agent.irl_config import PROMPTS as IRL_PROMPTS
from blueprints.orchestrator.agent.irl_config import MCP_CODE_INPUTS as IRL_MCP_CODE_INPUTS

# プラスチックエージェント用
from blueprints.orchestrator.agent.plastic_config import MCP_SERVERS as PLASTIC_MCP_SERVERS
from blueprints.orchestrator.agent.plastic_config import PROMPTS as PLASTIC_PROMPTS
from blueprints.orchestrator.agent.plastic_config import MCP_CODE_INPUTS as PLASTIC_MCP_CODE_INPUTS

# 関税エージェント用
from blueprints.orchestrator.agent.tariff_config import MCP_SERVERS as TARIFF_MCP_SERVERS
from blueprints.orchestrator.agent.tariff_config import PROMPTS as TARIFF_PROMPTS
from blueprints.orchestrator.agent.tariff_config import MCP_CODE_INPUTS as TARIFF_MCP_CODE_INPUTS

# プラスチックエージェントとIRLエージェント用
from blueprints.orchestrator.agent.product_config import MCP_SERVERS as PRODUCT_MCP_SERVERS
from blueprints.orchestrator.agent.product_config import PROMPTS as PRODUCT_PROMPTS
from blueprints.orchestrator.agent.product_config import MCP_CODE_INPUTS as PRODUCT_MCP_CODE_INPUTS

# Google検索エージェント用
from blueprints.orchestrator.agent.google_config import MCP_SERVERS as GOOGLE_MCP_SERVERS
from blueprints.orchestrator.agent.google_config import PROMPTS as GOOGLE_PROMPTS
from blueprints.orchestrator.agent.google_config import MCP_CODE_INPUTS as GOOGLE_MCP_CODE_INPUTS

# 企業投資調査:企業特定エージェント用
from blueprints.orchestrator.agent.company_info_config import MCP_SERVERS as COMPANY_INFO_MCP_SERVERS
from blueprints.orchestrator.agent.company_info_config import PROMPTS as COMPANY_INFO_PROMPTS
from blueprints.orchestrator.agent.company_info_config import MCP_CODE_INPUTS as COMPANY_INFO_MCP_CODE_INPUTS

# 企業投資調査:企業詳細調査エージェント用
from blueprints.orchestrator.agent.company_research_config import MCP_SERVERS as COMPANY_RESEARCH_MCP_SERVERS
from blueprints.orchestrator.agent.company_research_config import PROMPTS as COMPANY_RESEARCH_PROMPTS
from blueprints.orchestrator.agent.company_research_config import MCP_CODE_INPUTS as COMPANY_RESEARCH_MCP_CODE_INPUTS

# 監査予備調査:フローチャート作成エージェント用
from blueprints.orchestrator.agent.audit_flowchart_config import MCP_SERVERS as AUDIT_FLOWCHART_MCP_SERVERS
from blueprints.orchestrator.agent.audit_flowchart_config import PROMPTS as AUDIT_FLOWCHART_PROMPTS
from blueprints.orchestrator.agent.audit_flowchart_config import MCP_CODE_INPUTS as AUDIT_FLOWCHART_MCP_CODE_INPUTS

# 不正会計エージェント用
from blueprints.orchestrator.agent.accounting_fraud_config import MCP_SERVERS as ACCOUNTING_FRAUD_MCP_SERVERS
from blueprints.orchestrator.agent.accounting_fraud_config import PROMPTS as ACCOUNTING_FRAUD_PROMPTS
from blueprints.orchestrator.agent.accounting_fraud_config import MCP_CODE_INPUTS as ACCOUNTING_FRAUD_MCP_CODE_INPUTS

# 財務部問い合わせ支援用
from blueprints.orchestrator.agent.finance_department_config import MCP_SERVERS as FINANCE_DEPARTMENT_MCP_SERVERS
from blueprints.orchestrator.agent.finance_department_config import PROMPTS as FINANCE_DEPARTMENT_PROMPTS
from blueprints.orchestrator.agent.finance_department_config import MCP_CODE_INPUTS as FINANCE_DEPARTMENT_MCP_CODE_INPUTS

# 海外出向エージェント用
from blueprints.orchestrator.agent.expat_reimbursement_config import MCP_SERVERS as EXPAT_REIMBURSEMENT_MCP_SERVERS
from blueprints.orchestrator.agent.expat_reimbursement_config import PROMPTS as EXPAT_REIMBURSEMENT_PROMPTS
from blueprints.orchestrator.agent.expat_reimbursement_config import MCP_CODE_INPUTS as EXPAT_REIMBURSEMENT_MCP_CODE_INPUTS
from blueprints.orchestrator.agent.expat_reimbursement_config import SUMMARIZE_THRESHOLD as EXPAT_REIMBURSEMENT_SUMMARIZE_THRESHOLD

# HANAエージェント用
from blueprints.orchestrator.agent.hana_config import MCP_SERVERS as HANA_MCP_SERVERS
from blueprints.orchestrator.agent.hana_config import PROMPTS as HANA_PROMPTS
from blueprints.orchestrator.agent.hana_config import MCP_CODE_INPUTS as HANA_MCP_CODE_INPUTS

# マーケ支援エージェント用(market_analyst)
from blueprints.orchestrator.agent.market_analyst_config import MCP_SERVERS as MARKET_ANALYST_MCP_SERVERS
from blueprints.orchestrator.agent.market_analyst_config import PROMPTS as MARKET_ANALYST_PROMPTS
from blueprints.orchestrator.agent.market_analyst_config import MCP_CODE_INPUTS as MARKET_ANALYST_MCP_CODE_INPUTS

# マーケ支援エージェント用(competitor_analyst)
from blueprints.orchestrator.agent.competitor_analyst_config import MCP_SERVERS as COMPETITOR_ANALYST_MCP_SERVERS
from blueprints.orchestrator.agent.competitor_analyst_config import PROMPTS as COMPETITOR_ANALYST_PROMPTS
from blueprints.orchestrator.agent.competitor_analyst_config import MCP_CODE_INPUTS as COMPETITOR_ANALYST_MCP_CODE_INPUTS

# マーケ支援エージェント用(customer_analyst)
from blueprints.orchestrator.agent.customer_analyst_config import MCP_SERVERS as CUSTOMER_ANALYST_MCP_SERVERS
from blueprints.orchestrator.agent.customer_analyst_config import PROMPTS as CUSTOMER_ANALYST_PROMPTS
from blueprints.orchestrator.agent.customer_analyst_config import MCP_CODE_INPUTS as CUSTOMER_ANALYST_MCP_CODE_INPUTS

# マーケ支援エージェント用(target_analyst)
from blueprints.orchestrator.agent.target_analyst_config import MCP_SERVERS as TARGET_ANALYST_MCP_SERVERS
from blueprints.orchestrator.agent.target_analyst_config import PROMPTS as TARGET_ANALYST_PROMPTS
from blueprints.orchestrator.agent.target_analyst_config import MCP_CODE_INPUTS as TARGET_ANALYST_MCP_CODE_INPUTS

# マーケ支援エージェント用(idea_generator)
from blueprints.orchestrator.agent.idea_generator_config import MCP_SERVERS as IDEA_GENERATOR_MCP_SERVERS
from blueprints.orchestrator.agent.idea_generator_config import PROMPTS as IDEA_GENERATOR_PROMPTS
from blueprints.orchestrator.agent.idea_generator_config import MCP_CODE_INPUTS as IDEA_GENERATOR_MCP_CODE_INPUTS

# マーケ支援エージェント用(marketing_support_integrator)
from blueprints.orchestrator.agent.marketing_support_integrator_config import MCP_SERVERS as MARKETING_SUPPORT_INTEGRATOR_MCP_SERVERS
from blueprints.orchestrator.agent.marketing_support_integrator_config import PROMPTS as MARKETING_SUPPORT_INTEGRATOR_PROMPTS
from blueprints.orchestrator.agent.marketing_support_integrator_config import MCP_CODE_INPUTS as MARKETING_SUPPORT_INTEGRATOR_MCP_CODE_INPUTS

AGENT_CONFIG = {
    "default": {
        "submode": False,
        "servers": DEFAULT_MCP_SERVERS,
        "prompts": DEFAULT_PROMPTS,
        "code_inputs": DEFAULT_MCP_CODE_INPUTS,
    },
    "genie_agent": {
        "submode": True,
        "servers": GENIE_AGENT_MCP_SERVERS,
        "prompts": GENIE_AGENT_PROMPTS,
        "code_inputs": GENIE_AGENT_MCP_CODE_INPUTS,
    },
    "research": {
        "submode": True,
        "servers": RESEARCH_MCP_SERVERS,
        "prompts": RESEARCH_PROMPTS,
        "code_inputs": RESEARCH_MCP_CODE_INPUTS,
    },
    "audit_precheck": {
        "servers": AUDIT_PRECHECK_MCP_SERVERS,
        "prompts": AUDIT_PRECHECK_PROMPTS,
        "code_inputs": AUDIT_PRECHECK_MCP_CODE_INPUTS,
    },
    "panel_sales_enquiry": {
        "servers": PANEL_SALES_ENQUIRY_MCP_SERVERS,
        "prompts": PANEL_SALES_ENQUIRY_PROMPTS,
        "code_inputs": PANEL_SALES_ENQUIRY_MCP_CODE_INPUTS,
    },
    "irl": {
        "servers": IRL_MCP_SERVERS,
        "prompts": IRL_PROMPTS,
        "code_inputs": IRL_MCP_CODE_INPUTS,
    },
    "plastic": {
        "servers": PLASTIC_MCP_SERVERS,
        "prompts": PLASTIC_PROMPTS,
        "code_inputs": PLASTIC_MCP_CODE_INPUTS,
    },
    "tariff": {
        "servers": TARIFF_MCP_SERVERS,
        "prompts": TARIFF_PROMPTS,
        "code_inputs": TARIFF_MCP_CODE_INPUTS,
    },
    "product": {
        "servers": PRODUCT_MCP_SERVERS,
        "prompts": PRODUCT_PROMPTS,
        "code_inputs": PRODUCT_MCP_CODE_INPUTS,
    },
    "web_search": {
        "submode": True,
        "servers": GOOGLE_MCP_SERVERS,
        "prompts": GOOGLE_PROMPTS,
        "code_inputs": GOOGLE_MCP_CODE_INPUTS,
    },
    "company_info": {
        "servers": COMPANY_INFO_MCP_SERVERS,
        "prompts": COMPANY_INFO_PROMPTS,
        "code_inputs": COMPANY_INFO_MCP_CODE_INPUTS,
    },
    "company_research": {
        "servers": COMPANY_RESEARCH_MCP_SERVERS,
        "prompts": COMPANY_RESEARCH_PROMPTS,
        "code_inputs": COMPANY_RESEARCH_MCP_CODE_INPUTS,
    },
    "audit_flowchart": {
        "servers": AUDIT_FLOWCHART_MCP_SERVERS,
        "prompts": AUDIT_FLOWCHART_PROMPTS,
        "code_inputs": AUDIT_FLOWCHART_MCP_CODE_INPUTS,
    },
    "accounting_fraud": {
        "servers": ACCOUNTING_FRAUD_MCP_SERVERS,
        "prompts": ACCOUNTING_FRAUD_PROMPTS,
        "code_inputs": ACCOUNTING_FRAUD_MCP_CODE_INPUTS,
    },
    "finance_department": {
        "servers": FINANCE_DEPARTMENT_MCP_SERVERS,
        "prompts": FINANCE_DEPARTMENT_PROMPTS,
        "code_inputs": FINANCE_DEPARTMENT_MCP_CODE_INPUTS,
    },
    "expat_reimbursement": {
        "servers": EXPAT_REIMBURSEMENT_MCP_SERVERS,
        "prompts": EXPAT_REIMBURSEMENT_PROMPTS,
        "code_inputs": EXPAT_REIMBURSEMENT_MCP_CODE_INPUTS,
        "summarize_threshold": EXPAT_REIMBURSEMENT_SUMMARIZE_THRESHOLD,
    },
    "hana": {
        "servers": HANA_MCP_SERVERS,
        "prompts": HANA_PROMPTS,
        "code_inputs": HANA_MCP_CODE_INPUTS,
    },
    "market_analyst": {
        "servers": MARKET_ANALYST_MCP_SERVERS,
        "prompts": MARKET_ANALYST_PROMPTS,
        "code_inputs": MARKET_ANALYST_MCP_CODE_INPUTS,
    },
        "competitor_analyst": {
        "servers": COMPETITOR_ANALYST_MCP_SERVERS,
        "prompts": COMPETITOR_ANALYST_PROMPTS,
        "code_inputs": COMPETITOR_ANALYST_MCP_CODE_INPUTS,
    },
        "customer_analyst": {
        "servers": CUSTOMER_ANALYST_MCP_SERVERS,
        "prompts": CUSTOMER_ANALYST_PROMPTS,
        "code_inputs": CUSTOMER_ANALYST_MCP_CODE_INPUTS,
    },
        "target_analyst": {
        "servers": TARGET_ANALYST_MCP_SERVERS,
        "prompts": TARGET_ANALYST_PROMPTS,
        "code_inputs": TARGET_ANALYST_MCP_CODE_INPUTS,
    },
        "idea_generator": {
        "servers": IDEA_GENERATOR_MCP_SERVERS,
        "prompts": IDEA_GENERATOR_PROMPTS,
        "code_inputs": IDEA_GENERATOR_MCP_CODE_INPUTS,
    },
        "marketing_support_integrator": {
        "servers": MARKETING_SUPPORT_INTEGRATOR_MCP_SERVERS,
        "prompts": MARKETING_SUPPORT_INTEGRATOR_PROMPTS,
        "code_inputs": MARKETING_SUPPORT_INTEGRATOR_MCP_CODE_INPUTS,
    }
}
