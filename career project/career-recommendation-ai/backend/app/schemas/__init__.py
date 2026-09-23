from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.schemas.student import (
    StudentProfileCreate, StudentProfileResponse,
    AcademicRecordCreate, AcademicRecordResponse,
    AptitudeScoreCreate, AptitudeScoreResponse,
    CareerInterestCreate, CareerInterestResponse,
    FullStudentProfileResponse
)
from app.schemas.portfolio import (
    StudentSkillCreate, StudentSkillUpdate, StudentSkillResponse,
    CertificationCreate, CertificationUpdate, CertificationResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse, SkillResponse
)
from app.schemas.recommendation import (
    CareerRoleResponse, CareerRecommendationResponse,
    RecommendationExplanationResponse, GenerateRecommendationRequest,
    CompareCareerRequest, SkillGapResponse, ProgressCreate,
    ProgressUpdate, ProgressResponse
)
