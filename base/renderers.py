from rest_framework.response import Response



def custom_response_renderer(
        data=None, status=None,
        status_code=None):
    """ Renderer to perform rendering of API response in generic format across
    the service.
    """

    return Response(
        {
            "status": status,
            "data": data,
        },
        status=status_code
    )
