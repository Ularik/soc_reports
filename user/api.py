from ninja import Router
from .models import CustomUser
from .schema import UserCreateSchema

router = Router()

@router.post('/user-create', response={200: str, 400: str})
def user_create(request, body: UserCreateSchema):
    password = body.dict().pop('password')
    user = CustomUser(**body.dict())
    user.set_password(password)
    user.save()
    print(user.username, 'created')
    return 200, 'user create'

