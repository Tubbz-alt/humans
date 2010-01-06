# autogenerated by genmsg_py from direction.msg. Do not edit.
import roslib.message
import struct

## \htmlinclude direction.msg.html

class direction(roslib.message.Message):
  _md5sum = "260b8897f970e5623bdcdc313ccbab8e"
  _type = "tele_mobile/direction"
  _has_header = False #flag to mark the presence of a Header object
  _full_text = """float64 x
float64 y
float64 reset
float64 zen
float64 xvel
float64 yvel
float64 avel
float64 zen_reset
float64 lock

"""
  __slots__ = ['x','y','reset','zen','xvel','yvel','avel','zen_reset','lock']
  _slot_types = ['float64','float64','float64','float64','float64','float64','float64','float64','float64']

  ## Constructor. Any message fields that are implicitly/explicitly
  ## set to None will be assigned a default value. The recommend
  ## use is keyword arguments as this is more robust to future message
  ## changes.  You cannot mix in-order arguments and keyword arguments.
  ##
  ## The available fields are:
  ##   x,y,reset,zen,xvel,yvel,avel,zen_reset,lock
  ##
  ## @param args: complete set of field values, in .msg order
  ## @param kwds: use keyword arguments corresponding to message field names
  ## to set specific fields. 
  def __init__(self, *args, **kwds):
    super(direction, self).__init__(*args, **kwds)
    #message fields cannot be None, assign default values for those that are
    if self.x is None:
      self.x = 0.
    if self.y is None:
      self.y = 0.
    if self.reset is None:
      self.reset = 0.
    if self.zen is None:
      self.zen = 0.
    if self.xvel is None:
      self.xvel = 0.
    if self.yvel is None:
      self.yvel = 0.
    if self.avel is None:
      self.avel = 0.
    if self.zen_reset is None:
      self.zen_reset = 0.
    if self.lock is None:
      self.lock = 0.

  ## internal API method
  def _get_types(self): return direction._slot_types

  ## serialize message into buffer
  ## @param buff StringIO: buffer
  def serialize(self, buff):
    try:
      buff.write(struct.pack('<9d', self.x, self.y, self.reset, self.zen, self.xvel, self.yvel, self.avel, self.zen_reset, self.lock))
    except struct.error, se: self._check_types(se)
    except TypeError, te: self._check_types(te)

  ## unpack serialized message in str into this message instance
  ## @param str str: byte array of serialized message
  def deserialize(self, str):
    try:
      end = 0
      start = end
      end += 72
      (self.x, self.y, self.reset, self.zen, self.xvel, self.yvel, self.avel, self.zen_reset, self.lock,) = struct.unpack('<9d',str[start:end])
      return self
    except struct.error, e:
      raise roslib.message.DeserializationError(e) #most likely buffer underfill


  ## serialize message with numpy array types into buffer
  ## @param buff StringIO: buffer
  ## @param numpy module: numpy python module
  def serialize_numpy(self, buff, numpy):
    try:
      buff.write(struct.pack('<9d', self.x, self.y, self.reset, self.zen, self.xvel, self.yvel, self.avel, self.zen_reset, self.lock))
    except struct.error, se: self._check_types(se)
    except TypeError, te: self._check_types(te)

  ## unpack serialized message in str into this message instance using numpy for array types
  ## @param str str: byte array of serialized message
  ## @param numpy module: numpy python module
  def deserialize_numpy(self, str, numpy):
    try:
      end = 0
      start = end
      end += 72
      (self.x, self.y, self.reset, self.zen, self.xvel, self.yvel, self.avel, self.zen_reset, self.lock,) = struct.unpack('<9d',str[start:end])
      return self
    except struct.error, e:
      raise roslib.message.DeserializationError(e) #most likely buffer underfill

