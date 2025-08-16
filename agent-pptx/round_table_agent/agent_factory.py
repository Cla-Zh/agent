from enum import Enum
from .agent_frm_base import AgentBase, AgentConfig, AgentType
from .scientist_agent import ScientistAgent
from .software_architect_agent import SoftwareArchitectAgent
from .manager_agent import ManagerAgent
from .financier_agent import FinancierAgent
from .entrepreneur_agent import EntrepreneurAgent
from .artist_agent import ArtistAgent


  

class AgentFactory:
    """Agent工厂类"""
    
    @staticmethod
    def create_agent(agent_type: AgentType, name: str, **kwargs) -> AgentBase:
        """创建指定类型的Agent"""
        agent_classes = {
            AgentType.SCIENTIST: ScientistAgent,
            AgentType.ENGINEER: SoftwareArchitectAgent,
            AgentType.LEADER: ManagerAgent,
            AgentType.FINANCIER: FinancierAgent,
            AgentType.ENTREPRENEUR: EntrepreneurAgent,
            AgentType.ARTIST: ArtistAgent
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"不支持的Agent类型: {agent_type}")
        
        return agent_class()
    
    @staticmethod
    def create_scientist(name: str = "Scientist", **kwargs) -> ScientistAgent:
        """创建科学家Agent"""
        return AgentFactory.create_agent(AgentType.SCIENTIST, name, **kwargs)
    
    @staticmethod
    def create_software_architect(name: str = "SoftwareArchitect", **kwargs) -> SoftwareArchitectAgent:
        """创建软件架构师Agent"""
        return AgentFactory.create_agent(AgentType.ENGINEER, name, **kwargs) 
    
    @staticmethod
    def create_manager(name: str = "Manager", **kwargs) -> ManagerAgent:
        """创建管理者Agent"""
        return AgentFactory.create_agent(AgentType.LEADER, name, **kwargs)
    
    @staticmethod
    def create_financier(name: str = "Financier", **kwargs) -> FinancierAgent:
        """创建金融家Agent"""
        return AgentFactory.create_agent(AgentType.FINANCIER, name, **kwargs)
    
    @staticmethod
    def create_entrepreneur(name: str = "Entrepreneur", **kwargs) -> EntrepreneurAgent:
        """创建创业者Agent"""
        return AgentFactory.create_agent(AgentType.ENTREPRENEUR, name, **kwargs)
    
    @staticmethod
    def create_artist(name: str = "Artist", **kwargs) -> ArtistAgent:  
        """创建艺术家Agent"""
        return AgentFactory.create_agent(AgentType.ARTIST, name, **kwargs)

