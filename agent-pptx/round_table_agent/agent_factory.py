from enum import Enum
from agent_frm_base import AgentBase, AgentConfig
from scientist_agent import ScientistAgent
from software_architect_agent import SoftwareArchitectAgent
from manager_agent import ManagerAgent
from financier_agent import FinancierAgent
from entrepreneur_agent import EntrepreneurAgent
from artist_agent import ArtistAgent


class AgentType(Enum):
    """Agent类型枚举"""
    SCIENTIST = "scientist"
    SOFTWARE_ARCHITECT = "software_architect"
    MANAGER = "manager"
    FINANCIER = "financier"
    ENTREPRENEUR = "entrepreneur"
    ARTIST = "artist"  

class AgentFactory:
    """Agent工厂类"""
    
    @staticmethod
    def create_agent(agent_type: AgentType, name: str, **kwargs) -> AgentBase:
        """创建指定类型的Agent"""
        config = AgentConfig(name=name, agent_type=agent_type, **kwargs)
        
        agent_classes = {
            AgentType.SCIENTIST: ScientistAgent,
            AgentType.SOFTWARE_ARCHITECT: SoftwareArchitectAgent,
            AgentType.MANAGER: ManagerAgent,
            AgentType.FINANCIER: FinancierAgent,
            AgentType.ENTREPRENEUR: EntrepreneurAgent,
            AgentType.ARTIST: ArtistAgent
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"不支持的Agent类型: {agent_type}")
        
        return agent_class(config)
    
    @staticmethod
    def create_scientist(name: str = "Scientist", **kwargs) -> ScientistAgent:
        """创建研究员Agent"""
        return AgentFactory.create_agent(AgentType.SCIENTIST, name, **kwargs)
    
    @staticmethod
    def create_software_architect(name: str = "SoftwareArchitect", **kwargs) -> SoftwareArchitectAgent:
        """创建编程Agent"""
        return AgentFactory.create_agent(AgentType.SOFTWARE_ARCHITECT, name, **kwargs) 
    
    @staticmethod
    def create_manager(name: str = "Manager", **kwargs) -> ManagerAgent:
        """创建助手Agent"""
        return AgentFactory.create_agent(AgentType.MANAGER, name, **kwargs)
    
    @staticmethod
    def create_financier(name: str = "Financier", **kwargs) -> FinancierAgent:
        """创建分析师Agent"""
        return AgentFactory.create_agent(AgentType.FINANCIER, name, **kwargs)
    
    @staticmethod
    def create_entrepreneur(name: str = "Entrepreneur", **kwargs) -> EntrepreneurAgent:
        """创建创业者Agent"""
        return AgentFactory.create_agent(AgentType.ENTREPRENEUR, name, **kwargs)
    
    @staticmethod
    def create_artist(name: str = "Artist", **kwargs) -> ArtistAgent:  
        """创建艺术家Agent"""
        return AgentFactory.create_agent(AgentType.ARTIST, name, **kwargs)

