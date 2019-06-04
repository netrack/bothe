import aiohttp.web
import io

from bothe.model import Model


class Push:
    """Handler that save the provided model to storage.

    Attributes:
        models -- container of models
    """
    def __init__(self, models):
        self.models = models

    async def __call__(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """HTTP handler to save the model.

        Args:
            req -- request with a model tar archive
        """
        name = req.match_info.get("name")
        tag = req.match_info.get("tag")

        if not req.can_read_body:
            raise aiohttp.web.HTTPBadRequest(text="request has no body")

        model_stream = io.BytesIO(await req.read())
        await self.models.save(name, tag, model_stream)

        return aiohttp.web.Response(status=aiohttp.web.HTTPCreated.status_code)


class Predict:
    """Handler that calls the model prediction.

    Attributes:
        models -- container of models
    """

    def __init__(self, models):
        self.models = models

    async def __call__(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """HTTP handler to calculate model predictions.

        Feed model with feature vectors and calculate predictions.

        Args:
            req -- request with a list of feature-vectors
        """
        name = req.match_info.get("name")
        tag = req.match_info.get("tag")

        if not req.can_read_body:
            raise aiohttp.web.HTTPBadRequest(text="request has no body")

        body = await req.json()
        model = await self.models.load(name, tag)

        predictions = model.predict(x=body["x"])
        return aiohttp.web.json_response(dict(y=predictions))


class List:
    """Handler that lists all available models.

    Attributes:
        models -- container of models
    """

    def __init__(self, models):
        self.models = models

    async def __call__(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """HTTP handler to list available models.

        List available models in the storage.

        Args:
            req -- empty request
        """
        models = await self.models.all()
        dicts = map(lambda m: m.todict(), models)
        return aiohttp.web.json_response(list(dicts))


class Remove:
    """Handler that removes a model."""

    def __init__(self, models):
        self.models = models

    async def __call__(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        name = req.match_info.get("name")
        tag = req.match_info.get("tag")

        await self.models.delete(name, tag)
        return aiohttp.web.Response(status=aiohttp.web.HTTPOk.status_code)