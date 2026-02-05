"""
Definição centralizada de endpoints da API do AdaLove.
"""


class Endpoints:
    """Endpoints da API v2 do AdaLove."""
    
    # Base URL (configurável via settings)
    BASE_URL = "https://apiv2.inteli.edu.br"
    
    # Autenticação (AWS Cognito)
    COGNITO_BASE = "https://adalove.auth.us-east-2.amazoncognito.com"
    OAUTH_TOKEN = f"{COGNITO_BASE}/oauth2/token"
    OAUTH_AUTHORIZE = f"{COGNITO_BASE}/oauth2/authorize"
    
    # Usuário
    USER_DETAILS = "/users/details"
    USER_MENUS = "/users/menus"
    
    # Seções (Semanas)
    SECTIONS = "/sections"
    SECTION_USERDATA = "/sections/{section_uuid}/userdata"
    
    # Atividades (Cards)
    SECTION_ACTIVITIES = "/student-course-descriptions/section/{section_uuid}"
    
    # Atividades - Detalhes
    STUDENT_ACTIVITY_DATA = "/student-activities/{student_activity_uuid}/activity/data"
    
    # Notificações
    NOTIFICATIONS = "/notifications"
    
    # Versão
    VERSIONS = "/versions"
    
    @staticmethod
    def section_userdata(section_uuid: str) -> str:
        """
        Retorna endpoint de userdata para uma seção.
        
        Args:
            section_uuid: UUID da seção
            
        Returns:
            Endpoint formatado
        """
        return Endpoints.SECTION_USERDATA.format(section_uuid=section_uuid)
    
    @staticmethod
    def section_activities(section_uuid: str) -> str:
        """
        Retorna endpoint de atividades para uma seção.
        
        Args:
            section_uuid: UUID da seção
            
        Returns:
            Endpoint formatado
        """
        return Endpoints.SECTION_ACTIVITIES.format(section_uuid=section_uuid)
    
    @staticmethod
    def student_activity_data(student_activity_uuid: str) -> str:
        """
        Retorna endpoint de dados detalhados de uma atividade.
        
        Args:
            student_activity_uuid: UUID da atividade do estudante
            
        Returns:
            Endpoint formatado
        """
        return Endpoints.STUDENT_ACTIVITY_DATA.format(student_activity_uuid=student_activity_uuid)
