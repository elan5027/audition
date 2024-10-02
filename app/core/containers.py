from dependency_injector import providers, containers

from app.core.config import BaseAppSettings

from app.services.user_service import UserService
from app.services.image_service import ImageService
from app.services.order_service import OrderService
from app.services.audition_service import AuditionService
from app.services.payment_service import PaymentService
from app.clients.s3_client import S3Client

# from app.clients.smtp_client import SMTPClient
from app.clients.paypal_client import PayPalClient
from app.db.dependencies import get_db
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.order_repository import OrderRepository
from app.db.repositories.audition_repository import AuditionRepository
from app.db.repositories.payment_repository import PaymentRepository
from app.core.redis import RedisLock, RedisCache


class Container(containers.DeclarativeContainer):
    config: BaseAppSettings = providers.Configuration()

    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.api",
            "app.api.v1",
            "app.core",
            "app.services",
            "app.db.repositories",
        ]
    )
    redis_lock = providers.Singleton(RedisLock)
    redis_cache = providers.Singleton(RedisCache)

    # clients
    s3_client = providers.Factory(
        S3Client,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        bucket=config.bucket,
        aws_region=config.aws_region,
    )
    # smtp_client = providers.Factory(
    #     SMTPClient,
    #     smtp_user = config.smtp_user,
    #     smtp_port = config.smtp_port,
    #     smtp_password = config.smtp_password,
    # )

    paypal_client = providers.Factory(PayPalClient, payment_key=config.payment_key)

    # repositories
    user_repository = providers.Factory(
        UserRepository,
    )

    order_repository = providers.Factory(
        OrderRepository,
    )

    audition_repository = providers.Factory(
        AuditionRepository,
    )

    payment_repository = providers.Factory(
        PaymentRepository,
    )

    # services
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        # smtp_client=smtp_client,
        key=config.user_key,
        iv=config.seed_key,
    )

    image_service = providers.Factory(ImageService, s3_client=s3_client)

    order_service = providers.Factory(OrderService, order_repository=order_repository)

    audition_service = providers.Factory(
        AuditionService, audition_repository=audition_repository
    )

    payment_service = providers.Factory(
        PaymentService,
        payment_repository=payment_repository,
        paypal_client=paypal_client,
    )
