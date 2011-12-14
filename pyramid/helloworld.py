from paste.httpserver import serve
from pyramid.config import Configurator
from pyramid.response import Response

def hello_world(request):
   return Response('Hello %(name)s!\nnumber: %(number)s' % request.matchdict)

if __name__ == '__main__':
   config = Configurator()
   config.add_route('hello', '/hello/{name}/{number}')
   config.add_view(hello_world, route_name='hello')
   app = config.make_wsgi_app()
   #serve(app, host='0.0.0.0')
   serve(app, host='localhost', port=8080)

