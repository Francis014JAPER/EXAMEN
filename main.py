from fastapi import FastAPI
import uvicorn
from models import PedidoInsert,PedidoPay,PedidoCancelado,PedidosConsulta,PedidosConfirmar
from dao import Conexion
from fastapi.responses import JSONResponse,Response,Any
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
app=FastAPI()
#Evento que indica el momento en que se crea una una conexion con la BD
@app.on_event('startup')
def startup():
    app.cn=Conexion()
    print('Conectando con la BD')

@app.on_event('shutdown')
def shutdown():
    app.cn.cerrar()
    print('Cerrando la conexion')
@app.get('/categorias')
def consultaGeneralCategorias():
    return app.cn.consultaCategorias()
@app.get('/')
def inicio():
    return {"mensaje":"Bienvenido a PedidosREST"}

@app.post('/pedidos')
def agregarPedido(pedido:PedidoInsert):
    #return {"mensaje":"Agregando un pedido"}
    salida=app.cn.agregarPedido(pedido)
    return salida
@app.put('/pedidos/{idPedido}/pagar')
def pagarPedido(idPedido:str,pedidoPay:PedidoPay)->Response:
    #return {"mensaje":f"Pagando el pedido con id:{idPedido}"}
    salida=app.cn.pagarPedido(idPedido,pedidoPay)
    return JSONResponse(content=salida)

@app.delete('/pedidos/{idPedido}/cancelar')
def cancelarPedido(idPedido:str,pedido:PedidoCancelado):
    #return {"mensaje":f"Cancelando el pedido con id:{idPedido}"}
    salida=app.cn.cancelarPedido(idPedido,pedido)
    return salida

@app.get('/pedidos',response_model=PedidosConsulta)
def consultaGeneralPedidos()->Any:
    salida=app.cn.consultaGeneralPedidos()
    return PedidosConsulta(**salida)

@app.put('/pedidos/{idPedido}/confirmar')
def confirmarPedido(idPedido:str,pedidoconfirmado:PedidosConfirmar)->Response:
    salida=app.cn.confirmarPedido(idPedido,pedidoconfirmado)
    return JSONResponse(content=salida)


if __name__ == '__main__':
    uvicorn.run("main:app",port=8000,reload=True)

