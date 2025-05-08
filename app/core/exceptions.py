from fastapi import HTTPException, status

class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kimlik doğrulama bilgileri geçersiz",
            headers={"WWW-Authenticate": "Bearer"},
        )

class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Kayıt bulunamadı"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Veritabanı işlemi başarısız"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        ) 