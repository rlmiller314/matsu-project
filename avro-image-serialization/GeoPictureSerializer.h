#ifndef GEOPICTURESERIALIZER_H
#define GEOPICTURESERIALIZER_H

#include <Python.h>
#include <structmember.h>
#include <numpy/arrayobject.h>

#include "boost/any.hpp"
#include "avro/Compiler.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "avro/Specific.hh"
#include "avro/Generic.hh"

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

namespace gpwm {
  enum ByteOrder {
    LittleEndian,
    BigEndian,
    NativeEndian,
    IgnoreEndian
  };

  struct ZeroSuppressed {
    int64_t index;
    std::vector<uint8_t> strip;
    ZeroSuppressed() {}
  };

  struct GeoPictureWithMetadata {
    std::map<std::string,std::string> metadata;
    std::vector<std::string> bands;
    int32_t height;
    int32_t width;
    int32_t depth;
    int32_t dtype;
    int32_t itemsize;
    int64_t nbytes;
    bool fortran;
    ByteOrder byteorder;
    std::vector<ZeroSuppressed> data;
  };
}

namespace avro {
  template<> struct codec_traits<gpwm::ByteOrder> {
    static void encode(Encoder& e, gpwm::ByteOrder v) {
      e.encodeEnum(v);
    }   
    static void decode(Decoder& d, gpwm::ByteOrder& v) {
      v = static_cast<gpwm::ByteOrder>(d.decodeEnum());
    }   
  };  

  template<> struct codec_traits<gpwm::ZeroSuppressed> {
    static void encode(Encoder &e, const gpwm::ZeroSuppressed &v) {
      avro::encode(e, v.index);
      avro::encode(e, v.strip);
    }
    static void decode(Decoder &d, gpwm::ZeroSuppressed &v) {
      avro::decode(d, v.index);
      avro::decode(d, v.strip);
    }
  };

  template<> struct codec_traits<gpwm::GeoPictureWithMetadata> {
    static void encode(Encoder &e, const gpwm::GeoPictureWithMetadata &v) {
      avro::encode(e, v.metadata);
      avro::encode(e, v.bands);
      avro::encode(e, v.height);
      avro::encode(e, v.width);
      avro::encode(e, v.depth);
      avro::encode(e, v.dtype);
      avro::encode(e, v.itemsize);
      avro::encode(e, v.nbytes);
      avro::encode(e, v.fortran);
      avro::encode(e, v.byteorder);
      avro::encode(e, v.data);
    }
    static void decode(Decoder &d, gpwm::GeoPictureWithMetadata &v) {
      avro::decode(d, v.metadata);
      avro::decode(d, v.bands);
      avro::decode(d, v.height);
      avro::decode(d, v.width);
      avro::decode(d, v.depth);
      avro::decode(d, v.dtype);
      avro::decode(d, v.itemsize);
      avro::decode(d, v.nbytes);
      avro::decode(d, v.fortran);
      avro::decode(d, v.byteorder);
      avro::decode(d, v.data);
    }
  };
}

typedef struct {
  PyObject_HEAD

  PyObject *schema;
  avro::ValidSchema validSchema;
  PyObject *metadata;
  PyObject *bands;
  PyObject *picture;

} GeoPictureSerializer_GeoPicture;

static int GeoPictureSerializer_GeoPicture_init(GeoPictureSerializer_GeoPicture *self);
static PyObject *GeoPictureSerializer_GeoPicture_serialize(GeoPictureSerializer_GeoPicture *self);
static PyObject *GeoPictureSerializer_deserialize(PyObject *args);

#endif // GEOPICTURESERIALIZER_H
