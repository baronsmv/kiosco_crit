from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from queries.utils import parse_form


class BaseConsultaAPIView(APIView):
    config_data = None
    form_class = None
    data_query = None
    nombre_objetos = ""
    nombre_sujeto = None
    nombre_id = None
    exist_query = None

    def post(self, request):
        form = self.form_class(request.data)
        context = {}

        try:
            parse_form(
                request=request,
                context=context,
                config_data=self.config_data,
                form=form,
                model=None,
                exist_query=self.exist_query,
                data_query=self.data_query,
                nombre_id=self.nombre_id,
                nombre_sujeto=self.nombre_sujeto,
                nombre_objetos=self.nombre_objetos,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "sujeto": context.get("sujeto"),
                "tabla": context.get("tabla"),
                "objetos": context.get("objetos"),
            },
            status=status.HTTP_200_OK,
        )
