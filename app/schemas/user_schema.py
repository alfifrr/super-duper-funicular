from dataclasses import dataclass
from typing import Optional


@dataclass
class UserSignupSchema:
    username: str
    email: str
    password: str

    @classmethod
    def validate(cls, data: dict) -> Optional['UserSignupSchema']:
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return None
        return cls(**{k: data[k] for k in required_fields})


@dataclass
class UserLoginSchema:
    username: str
    password: str

    @classmethod
    def validate(cls, data: dict) -> Optional['UserLoginSchema']:
        required_fields = ['username', 'password']
        if not all(field in data for field in required_fields):
            return None
        return cls(**{k: data[k] for k in required_fields})


@dataclass
class UserUpdateSchema:
    email: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def validate(cls, data: dict) -> 'UserUpdateSchema':
        validated_data = {}
        if 'email' in data:
            validated_data['email'] = data['email']
        if 'password' in data:
            validated_data['password'] = data['password']
        return cls(**validated_data)
