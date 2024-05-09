from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class DetallePedido(BaseModel):
    idProducto:int
    cantidad:int
    precio:float
    subtotal:float
    costoEnvio:float
    subtotalEnvio:float

class PedidoInsert(BaseModel):
    idComprador:int
    idVendedor:int
    fechaRegistro:datetime=Field(default=datetime.now())
    costosEnvio:float=Field(...,ge=0)
    subtotal:float=Field(...,gt=0)
    total:float=Field(...,gt=0)
    estatus:str=Field(default='Captura')
    detalle:list[DetallePedido]

class Pago(BaseModel):
    fecha:datetime=Field(default=datetime.now())
    monto:float=Field(ge=0)
    idTarjeta:int
    estatus:str=Field(default='Aprobado')

class PedidoPay(BaseModel):
    estatus:str=Field(default='Pagado')
    pago:Pago

class PedidoCancelado(BaseModel):
    estatus:str=Field(default="Cancelado")
    motivoCancelacion:str

class DetallePedidoConsulta(BaseModel):
    idProducto:int
    cantidad:int
    precio:float
    subtotal:float
    costoEnvio:float
    subtotalEnvio:float
    nombreProducto:str

class PagoConsulta(BaseModel):
    fecha:datetime
    monto:float
    idTarjeta:int
    estatus:str
    noTarjeta:str

class Comprador(BaseModel):
    idComprador:int
    nombre:str

class Vendedor(BaseModel):
    idVendedor:int
    nombre:str

class Pedido(BaseModel):
    idPedido:str
    fechaRegistro:datetime
    fechaConfirmacion:datetime|None=None
    fechaCierre:datetime|None=None
    costosEnvio:float
    subtotal:float
    total:float
    estatus:str
    motivoCancelacion:str|None=None
    valoracion:int|None=None
    detalles:list[DetallePedidoConsulta]
    pago:PagoConsulta| None=None
    comprador:Comprador
    vendedor:Vendedor

class PedidosConsulta(BaseModel):
    estatus:str
    mensaje:str
    pedidos:list[Pedido]

class detalleEnvioConfirmado(BaseModel):
    idProducto:int
    cantidadEnviada:int

class envioConfirmado(BaseModel):
    fechaSalida:datetime=Field(default=datetime.now())
    fechaEntPlan:datetime=Field(default=datetime.now())
    noGuia:str
    idPaqueteria:int
    detalle:list[detalleEnvioConfirmado]
    
class PedidosConfirmar(BaseModel):
    estatus:str=Field(default='Confirmado')
    fechaConfirmacion:datetime=Field(default=datetime.now())
    envio:list[envioConfirmado]

    #EXAMEN
class detalleEnvioConfirmado(BaseModel):
    idProducto:int
    cantidadEnviada:int

class envioConfirmado(BaseModel):
    fechaSalida:datetime=Field(default=datetime.now())
    fechaEntPlan:datetime=Field(default=datetime.now())
    noGuia:str
    idPaqueteria:int
    detalle:list[detalleEnvioConfirmado]

#SI ENVIO CONFIRMADO FUERA OTRO ARREGLO TENGO QUE RECORRER OTRO ARREGLO O COMO ACCEDO A UN ARREGLO DENTRO DE OTRO?    
class PedidosConfirmar(BaseModel):
    estatus:str=Field(default='Confirmado')
    fechaConfirmacion:datetime=Field(default=datetime.now())
    envio:envioConfirmado
