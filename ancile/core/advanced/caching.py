from RestrictedPython import compile_restricted_exec
import dill


def retrieve_compiled(program, redis):
    redis_response = redis.get(program) if ENABLE_CACHE else None

    if redis_response is None:
        compile_results = compile_restricted_exec(program)
        if compile_results.errors:
            raise AncileException(compile_results.errors)
        if ENABLE_CACHE:
            redis.set(program, dill.dumps(compile_results.code), ex=600)
            logger.debug("Cache miss on submitted program")
        return compile_results.code
    logger.debug("Used cached program")
    return dill.loads(redis_response)
