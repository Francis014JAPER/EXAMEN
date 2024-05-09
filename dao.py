from pymongo import MongoClient
from models import PedidoInsert,PedidoPay,PedidoCancelado,PedidosConfirmar
from datetime import datetime
from bson import ObjectId,DatetimeConversion
from time import strftime
class Conexion():
    def __init__(self):
        self.cliente=MongoClient()
        self.bd=self.cliente.ShopiteszREST
    def cerrar(self):
        self.cliente.close()
    def consultaCategorias(self):
        return list(self.bd.categorias.find())
    def agregarPedido(self,pedido:PedidoInsert):
        respuesta={"estatus":"","mensaje":""}
        if(pedido.idComprador!=pedido.idVendedor):
            if self.comprobarUsuario(pedido.idComprador,"Comprador")>0 and self.comprobarUsuario(pedido.idVendedor,"Vendedor")>0:
                ban=True
                for dp in pedido.detalle:
                    if self.comprobarProducto(dp.idProducto,pedido.idVendedor,dp.cantidad)==0:
                        ban=False
                        break
                if ban:
                    res=self.bd.pedidos.insert_one(pedido.dict())
                    respuesta["estatus"]="OK"
                    respuesta["mensaje"]="Pedido agregado con exito con id:"\
                                 +str(res.inserted_id)
                    respuesta["pedido"]=pedido
                else:
                    respuesta["estatus"]="Error"
                    respuesta["mensaje"]="El pedido no se puede registrar por que " \
                                         "no existe la cantidad suficiente del producto "
            else:
                respuesta["estatus"]="Error"
                respuesta["mensaje"]="El comprador o el vendedor no existen"
        else:
            respuesta["estatus"]="Error"
            respuesta["mensaje"]="El comprador y el vendedor deben ser diferentes"
        return respuesta
    def comprobarUsuario(self,idUsuario,tipo):
        cont=self.bd.usuarios.count_documents({"_id":idUsuario,"tipo":tipo})
        return cont
    def comprobarProducto(self,idProducto,idVendedor,cantidad):
        cont=self.bd.productos.count_documents({"_id":idProducto,
                "idVendedor":idVendedor,"existencia":{"$gte":cantidad}})
        return cont
    def pagarPedido(self,idPedido,pedidoPay:PedidoPay):
        pedido=self.comprobarPedido(idPedido)
        resp={"estatus":"","mensaje":""}
        if pedido:
            if pedido['total']==pedidoPay.pago.monto:
                cont=self.comprobarTarjeta(pedidoPay.pago.idTarjeta,pedido['idComprador'])
                if cont>0:
                    res=self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},{"$set":pedidoPay.dict()})
                    if res.modified_count>0:
                        resp["estatus"]="OK"
                        resp["mensaje"]=f'El pago del pedido con id:{idPedido} se realizo con exito'
                    else:
                        resp['estatus']='Error'
                        resp['mensaje']=f'Error al efectuar el pago del pedido con id:{idPedido}, intente mas tarde'
                else:
                    resp['estatus']='Error'
                    resp['mensaje']='Error al efectuar el pago, debido a que no existe la tarjeta'
            else:
                resp['estatus']='Error'
                resp['mensaje']='Error al efectuar el pago, el monto no cubre el total del pedido'
        else:
            resp['estatus']='Error'
            resp['mensaje']='Error al efectuar el pago, el pedido no existe o no se encuentra en captura'
        return resp
    def comprobarTarjeta(self,idTarjeta,idComprador):
        fechaActual=datetime.now()
        cont=self.bd.usuarios.count_documents({"_id":idComprador,
                                               "tarjetas.idTarjeta":idTarjeta,
                                               "tarjetas.estatus":'A',
                                               "tarjetas.fechaVencimiento":{"$gte":fechaActual}})
        return cont
    def comprobarPedido(self,idPedido):
        pedido=self.bd.pedidos.find_one({"_id":ObjectId(idPedido),
                                         "estatus":"Captura"},
                                        projection={"idComprador":True,"total":True})
        return pedido

    def cancelarPedido(self,idPedido,cancelacion:PedidoCancelado):
        pedido=self.bd.pedidos.find_one({"_id":ObjectId(idPedido)},
                                        projection={"estatus":True})
        resp={"estatus":"","mensaje":""}
        if pedido:
            if pedido['estatus']=='Captura' or pedido["estatus"]=='Pagado':
                res=self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},
                                               {"$set":cancelacion.dict()})
                if pedido['estatus']=='Pagado':
                    self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},
                                               {"$set":{"pago.estatus":"Devolucion"}})
                resp["estatus"]="OK"
                resp["mensaje"]=f"Pedido con id:{idPedido} cancelado con exito"
            else:
                resp["estatus"]="Error"
                resp["mensaje"]="El pedido no se puede cancelar porque se encuentra en proceso"
        else:
            resp["estatus"]="Error"
            resp["mensaje"]="El pedido no existe"
        return resp
    
    def consultaGeneralPedidos(self):
        resp={"estatus":"","mensaje":""}
        resultado=self.bd.consultaPedidos.find({})
        resp["estatus"]="OK"
        resp["mensaje"]="Listado de Pedidos"
        lista=[]
        for ped in resultado:
            ped["idPedido"]=str(ped['idPedido'])
            detalles=ped['detalles']
            detalleTemp=[]
            for prod in detalles:
                self.complementarDetalle(prod)
                detalleTemp.append(prod)
            ped['detalles']=detalleTemp
            if 'pago' in ped:
                pago=ped['pago']
                pago['noTarjeta']=self.ConsultarNoTarjeta(pago['idTarjeta'])
                ped['pago']=pago
            lista.append(ped)
        resp["pedidos"]=lista
        return resp
    
    def consultarProducto(self,idProducto):
        producto=self.bd.productos.find_one({"_id":idProducto})
        return producto
    
    def complementarDetalle(self,detalle):
        prod=self.consultarProducto(detalle['idProducto'])
        detalle['nombreProducto']=prod['nombre']
        return detalle
    
    def ConsultarNoTarjeta(self,idTarjeta):
        res=self.bd.usuarios.find_one({"tarjetas.idTarjeta":idTarjeta},
                                      projection={"tarjetas.$":1,"_id":0})
        tarjetas=res['tarjetas']
        tarjeta=tarjetas[0]
        return tarjeta['noTarjeta']
    
    def comprobarPedididoConfirmado(self,idPedido):
        pedido=self.bd.pedidos.find_one({"_id":ObjectId(idPedido),
                                         "estatus":"Pagado"})
        return pedido
    
    def comprobarCantidad(self,idPedido,idProducto,cantidad):
        pedido1=self.bd.pedidos.count_documents({"_id":idPedido,
                                               'detalle.idProducto':idProducto,
                                               'detalle.cantidad':cantidad,
                                              })
        return pedido1

    
    def confirmarPedido(self,idPedido,pedidoConf:PedidosConfirmar):
        resp={"estatus":"","mensaje":""}
        pedido = self.comprobarPedidoConfirmado(idPedido)
        arr=pedidoConf.envio.detalle
        if pedido:
            for o in arr:
                #MI LÓGICA ERA BUSCAR EN LA BD PRIMERO EL PEDIDO QUE FUERA A SER MODIFICADO Y DESPUES COMPRBARLO CON LOS ELEMENTOS INSERTADOS
                cantidad = self.comprobarCantidad(idPedido, o.idProducto, o.cantidadEnviada)
                if cantidad>0:
                        self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},{"$set":pedidoConf.dict()}) 
                        resp["estatus"]="Confirmado"
                        resp["mensaje"]="El pedido con id:{idPedido} esta entregado en la paqueteria "
                else:
                    resp["estatus"]="Error"
                    resp["mensaje"]="El pedido no se puede confirmar." 
        else:
            resp["estatus"]="Error"
            resp["mensaje"]="El pedido no se puede encontrar."                
        return resp

    def comprobarPedidoConfirmado(self,idPedido):
        pedido=self.bd.pedidos.find_one({"_id":ObjectId(idPedido),
                                         "estatus":"Pagado"})
        return pedido
    
    def comprobarCantidad(self,idPedido,idProducto,cantidad):
        cont=self.bd.pedidos.count_documents({"_id":ObjectId(idPedido),
                                               "detalle.idProducto":idProducto,
                                               "detalle.cantidad":cantidad,
                                              })
        return cont
        