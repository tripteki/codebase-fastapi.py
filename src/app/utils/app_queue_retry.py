from typing import Callable
import time
import functools
import logging

logger = logging.getLogger (__name__)

def retry (
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0
) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Args:
        max_retries (int)
        initial_delay (float)
        exponential_base (float)
        max_delay (float)
    Returns:
        Callable[[Callable[..., object]], Callable[..., object]]
    """
    def decorator (func: Callable[..., object]) -> Callable[..., object]:
        """
        Args:
            func (Callable[..., object])
        Returns:
            Callable[..., object]
        """
        @functools.wraps (func)
        def wrapper (*args: object, **kwargs: object) -> object:
            """
            Args:
                *args (object)
                **kwargs (object)
            Returns:
                object
            """
            last_exception = None

            for attempt in range (max_retries + 1):
                try:
                    return func (*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries:
                        delay = min (initial_delay * (exponential_base ** attempt), max_delay)

                        logger.warning (
                            f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {delay:.2f}s. Error: {str (e)}"
                        )

                        time.sleep (delay)
                    else:
                        logger.error (
                            f"Max retries ({max_retries}) exceeded for {func.__name__}. "
                            f"Final error: {str (e)}"
                        )

            raise last_exception

        return wrapper
    return decorator
