# 
import morpcc
import morpcc.permission as ccperm
import morpfw
from morpfw.authz.pas import DefaultAuthzPolicy
from morpfw.crud import permission as crudperm
# 

# 


class AppRoot(morpcc.Root):
    pass


class App(morpcc.App):
    pass


@App.path(model=AppRoot, path='/')
def get_approot(request):
    return AppRoot(request)


@App.html(model=AppRoot, template='contrace/index.pt',
          permission=ccperm.ViewHome)
def index(context, request):
    return {
        "message": "Hello world"
    }


@App.template_directory()
def get_template_directory():
    return 'templates'

# 
