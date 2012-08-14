package org.occ.matsu;

/**
 * Autogenerated by Avro
 * 
 * DO NOT EDIT DIRECTLY
 */
@SuppressWarnings("all")
public class GeoPictureWithMetadata extends org.apache.avro.specific.SpecificRecordBase implements org.apache.avro.specific.SpecificRecord {
  public static final org.apache.avro.Schema SCHEMA$ = new org.apache.avro.Schema.Parser().parse("{\"type\":\"record\",\"name\":\"GeoPictureWithMetadata\",\"fields\":[{\"name\":\"metadata\",\"type\":{\"type\":\"map\",\"values\":\"string\"}},{\"name\":\"bands\",\"type\":{\"type\":\"array\",\"items\":\"string\"}},{\"name\":\"height\",\"type\":\"int\"},{\"name\":\"width\",\"type\":\"int\"},{\"name\":\"depth\",\"type\":\"int\"},{\"name\":\"dtype\",\"type\":\"int\"},{\"name\":\"itemsize\",\"type\":\"int\"},{\"name\":\"nbytes\",\"type\":\"long\"},{\"name\":\"fortran\",\"type\":\"boolean\"},{\"name\":\"byteorder\",\"type\":{\"type\":\"enum\",\"name\":\"ByteOrder\",\"symbols\":[\"LittleEndian\",\"BigEndian\",\"NativeEndian\",\"IgnoreEndian\"]}},{\"name\":\"data\",\"type\":{\"type\":\"array\",\"items\":{\"type\":\"record\",\"name\":\"ZeroSuppressed\",\"fields\":[{\"name\":\"index\",\"type\":\"long\"},{\"name\":\"strip\",\"type\":\"bytes\"}]}}}]}");
  @Deprecated public java.util.Map<java.lang.CharSequence,java.lang.CharSequence> metadata;
  @Deprecated public java.util.List<java.lang.CharSequence> bands;
  @Deprecated public int height;
  @Deprecated public int width;
  @Deprecated public int depth;
  @Deprecated public int dtype;
  @Deprecated public int itemsize;
  @Deprecated public long nbytes;
  @Deprecated public boolean fortran;
  @Deprecated public ByteOrder byteorder;
  @Deprecated public java.util.List<ZeroSuppressed> data;
  public org.apache.avro.Schema getSchema() { return SCHEMA$; }
  // Used by DatumWriter.  Applications should not call. 
  public java.lang.Object get(int field$) {
    switch (field$) {
    case 0: return metadata;
    case 1: return bands;
    case 2: return height;
    case 3: return width;
    case 4: return depth;
    case 5: return dtype;
    case 6: return itemsize;
    case 7: return nbytes;
    case 8: return fortran;
    case 9: return byteorder;
    case 10: return data;
    default: throw new org.apache.avro.AvroRuntimeException("Bad index");
    }
  }
  // Used by DatumReader.  Applications should not call. 
  @SuppressWarnings(value="unchecked")
  public void put(int field$, java.lang.Object value$) {
    switch (field$) {
    case 0: metadata = (java.util.Map<java.lang.CharSequence,java.lang.CharSequence>)value$; break;
    case 1: bands = (java.util.List<java.lang.CharSequence>)value$; break;
    case 2: height = (java.lang.Integer)value$; break;
    case 3: width = (java.lang.Integer)value$; break;
    case 4: depth = (java.lang.Integer)value$; break;
    case 5: dtype = (java.lang.Integer)value$; break;
    case 6: itemsize = (java.lang.Integer)value$; break;
    case 7: nbytes = (java.lang.Long)value$; break;
    case 8: fortran = (java.lang.Boolean)value$; break;
    case 9: byteorder = (ByteOrder)value$; break;
    case 10: data = (java.util.List<ZeroSuppressed>)value$; break;
    default: throw new org.apache.avro.AvroRuntimeException("Bad index");
    }
  }

  /**
   * Gets the value of the 'metadata' field.
   */
  public java.util.Map<java.lang.CharSequence,java.lang.CharSequence> getMetadata() {
    return metadata;
  }

  /**
   * Sets the value of the 'metadata' field.
   * @param value the value to set.
   */
  public void setMetadata(java.util.Map<java.lang.CharSequence,java.lang.CharSequence> value) {
    this.metadata = value;
  }

  /**
   * Gets the value of the 'bands' field.
   */
  public java.util.List<java.lang.CharSequence> getBands() {
    return bands;
  }

  /**
   * Sets the value of the 'bands' field.
   * @param value the value to set.
   */
  public void setBands(java.util.List<java.lang.CharSequence> value) {
    this.bands = value;
  }

  /**
   * Gets the value of the 'height' field.
   */
  public java.lang.Integer getHeight() {
    return height;
  }

  /**
   * Sets the value of the 'height' field.
   * @param value the value to set.
   */
  public void setHeight(java.lang.Integer value) {
    this.height = value;
  }

  /**
   * Gets the value of the 'width' field.
   */
  public java.lang.Integer getWidth() {
    return width;
  }

  /**
   * Sets the value of the 'width' field.
   * @param value the value to set.
   */
  public void setWidth(java.lang.Integer value) {
    this.width = value;
  }

  /**
   * Gets the value of the 'depth' field.
   */
  public java.lang.Integer getDepth() {
    return depth;
  }

  /**
   * Sets the value of the 'depth' field.
   * @param value the value to set.
   */
  public void setDepth(java.lang.Integer value) {
    this.depth = value;
  }

  /**
   * Gets the value of the 'dtype' field.
   */
  public java.lang.Integer getDtype() {
    return dtype;
  }

  /**
   * Sets the value of the 'dtype' field.
   * @param value the value to set.
   */
  public void setDtype(java.lang.Integer value) {
    this.dtype = value;
  }

  /**
   * Gets the value of the 'itemsize' field.
   */
  public java.lang.Integer getItemsize() {
    return itemsize;
  }

  /**
   * Sets the value of the 'itemsize' field.
   * @param value the value to set.
   */
  public void setItemsize(java.lang.Integer value) {
    this.itemsize = value;
  }

  /**
   * Gets the value of the 'nbytes' field.
   */
  public java.lang.Long getNbytes() {
    return nbytes;
  }

  /**
   * Sets the value of the 'nbytes' field.
   * @param value the value to set.
   */
  public void setNbytes(java.lang.Long value) {
    this.nbytes = value;
  }

  /**
   * Gets the value of the 'fortran' field.
   */
  public java.lang.Boolean getFortran() {
    return fortran;
  }

  /**
   * Sets the value of the 'fortran' field.
   * @param value the value to set.
   */
  public void setFortran(java.lang.Boolean value) {
    this.fortran = value;
  }

  /**
   * Gets the value of the 'byteorder' field.
   */
  public ByteOrder getByteorder() {
    return byteorder;
  }

  /**
   * Sets the value of the 'byteorder' field.
   * @param value the value to set.
   */
  public void setByteorder(ByteOrder value) {
    this.byteorder = value;
  }

  /**
   * Gets the value of the 'data' field.
   */
  public java.util.List<ZeroSuppressed> getData() {
    return data;
  }

  /**
   * Sets the value of the 'data' field.
   * @param value the value to set.
   */
  public void setData(java.util.List<ZeroSuppressed> value) {
    this.data = value;
  }

  /** Creates a new GeoPictureWithMetadata RecordBuilder */
  public static GeoPictureWithMetadata.Builder newBuilder() {
    return new GeoPictureWithMetadata.Builder();
  }
  
  /** Creates a new GeoPictureWithMetadata RecordBuilder by copying an existing Builder */
  public static GeoPictureWithMetadata.Builder newBuilder(GeoPictureWithMetadata.Builder other) {
    return new GeoPictureWithMetadata.Builder(other);
  }
  
  /** Creates a new GeoPictureWithMetadata RecordBuilder by copying an existing GeoPictureWithMetadata instance */
  public static GeoPictureWithMetadata.Builder newBuilder(GeoPictureWithMetadata other) {
    return new GeoPictureWithMetadata.Builder(other);
  }
  
  /**
   * RecordBuilder for GeoPictureWithMetadata instances.
   */
  public static class Builder extends org.apache.avro.specific.SpecificRecordBuilderBase<GeoPictureWithMetadata>
    implements org.apache.avro.data.RecordBuilder<GeoPictureWithMetadata> {

    private java.util.Map<java.lang.CharSequence,java.lang.CharSequence> metadata;
    private java.util.List<java.lang.CharSequence> bands;
    private int height;
    private int width;
    private int depth;
    private int dtype;
    private int itemsize;
    private long nbytes;
    private boolean fortran;
    private ByteOrder byteorder;
    private java.util.List<ZeroSuppressed> data;

    /** Creates a new Builder */
    private Builder() {
      super(GeoPictureWithMetadata.SCHEMA$);
    }
    
    /** Creates a Builder by copying an existing Builder */
    private Builder(GeoPictureWithMetadata.Builder other) {
      super(other);
    }
    
    /** Creates a Builder by copying an existing GeoPictureWithMetadata instance */
    private Builder(GeoPictureWithMetadata other) {
            super(GeoPictureWithMetadata.SCHEMA$);
      if (isValidValue(fields()[0], other.metadata)) {
        this.metadata = (java.util.Map<java.lang.CharSequence,java.lang.CharSequence>) data().deepCopy(fields()[0].schema(), other.metadata);
        fieldSetFlags()[0] = true;
      }
      if (isValidValue(fields()[1], other.bands)) {
        this.bands = (java.util.List<java.lang.CharSequence>) data().deepCopy(fields()[1].schema(), other.bands);
        fieldSetFlags()[1] = true;
      }
      if (isValidValue(fields()[2], other.height)) {
        this.height = (java.lang.Integer) data().deepCopy(fields()[2].schema(), other.height);
        fieldSetFlags()[2] = true;
      }
      if (isValidValue(fields()[3], other.width)) {
        this.width = (java.lang.Integer) data().deepCopy(fields()[3].schema(), other.width);
        fieldSetFlags()[3] = true;
      }
      if (isValidValue(fields()[4], other.depth)) {
        this.depth = (java.lang.Integer) data().deepCopy(fields()[4].schema(), other.depth);
        fieldSetFlags()[4] = true;
      }
      if (isValidValue(fields()[5], other.dtype)) {
        this.dtype = (java.lang.Integer) data().deepCopy(fields()[5].schema(), other.dtype);
        fieldSetFlags()[5] = true;
      }
      if (isValidValue(fields()[6], other.itemsize)) {
        this.itemsize = (java.lang.Integer) data().deepCopy(fields()[6].schema(), other.itemsize);
        fieldSetFlags()[6] = true;
      }
      if (isValidValue(fields()[7], other.nbytes)) {
        this.nbytes = (java.lang.Long) data().deepCopy(fields()[7].schema(), other.nbytes);
        fieldSetFlags()[7] = true;
      }
      if (isValidValue(fields()[8], other.fortran)) {
        this.fortran = (java.lang.Boolean) data().deepCopy(fields()[8].schema(), other.fortran);
        fieldSetFlags()[8] = true;
      }
      if (isValidValue(fields()[9], other.byteorder)) {
        this.byteorder = (ByteOrder) data().deepCopy(fields()[9].schema(), other.byteorder);
        fieldSetFlags()[9] = true;
      }
      if (isValidValue(fields()[10], other.data)) {
        this.data = (java.util.List<ZeroSuppressed>) data().deepCopy(fields()[10].schema(), other.data);
        fieldSetFlags()[10] = true;
      }
    }

    /** Gets the value of the 'metadata' field */
    public java.util.Map<java.lang.CharSequence,java.lang.CharSequence> getMetadata() {
      return metadata;
    }
    
    /** Sets the value of the 'metadata' field */
    public GeoPictureWithMetadata.Builder setMetadata(java.util.Map<java.lang.CharSequence,java.lang.CharSequence> value) {
      validate(fields()[0], value);
      this.metadata = value;
      fieldSetFlags()[0] = true;
      return this; 
    }
    
    /** Checks whether the 'metadata' field has been set */
    public boolean hasMetadata() {
      return fieldSetFlags()[0];
    }
    
    /** Clears the value of the 'metadata' field */
    public GeoPictureWithMetadata.Builder clearMetadata() {
      metadata = null;
      fieldSetFlags()[0] = false;
      return this;
    }

    /** Gets the value of the 'bands' field */
    public java.util.List<java.lang.CharSequence> getBands() {
      return bands;
    }
    
    /** Sets the value of the 'bands' field */
    public GeoPictureWithMetadata.Builder setBands(java.util.List<java.lang.CharSequence> value) {
      validate(fields()[1], value);
      this.bands = value;
      fieldSetFlags()[1] = true;
      return this; 
    }
    
    /** Checks whether the 'bands' field has been set */
    public boolean hasBands() {
      return fieldSetFlags()[1];
    }
    
    /** Clears the value of the 'bands' field */
    public GeoPictureWithMetadata.Builder clearBands() {
      bands = null;
      fieldSetFlags()[1] = false;
      return this;
    }

    /** Gets the value of the 'height' field */
    public java.lang.Integer getHeight() {
      return height;
    }
    
    /** Sets the value of the 'height' field */
    public GeoPictureWithMetadata.Builder setHeight(int value) {
      validate(fields()[2], value);
      this.height = value;
      fieldSetFlags()[2] = true;
      return this; 
    }
    
    /** Checks whether the 'height' field has been set */
    public boolean hasHeight() {
      return fieldSetFlags()[2];
    }
    
    /** Clears the value of the 'height' field */
    public GeoPictureWithMetadata.Builder clearHeight() {
      fieldSetFlags()[2] = false;
      return this;
    }

    /** Gets the value of the 'width' field */
    public java.lang.Integer getWidth() {
      return width;
    }
    
    /** Sets the value of the 'width' field */
    public GeoPictureWithMetadata.Builder setWidth(int value) {
      validate(fields()[3], value);
      this.width = value;
      fieldSetFlags()[3] = true;
      return this; 
    }
    
    /** Checks whether the 'width' field has been set */
    public boolean hasWidth() {
      return fieldSetFlags()[3];
    }
    
    /** Clears the value of the 'width' field */
    public GeoPictureWithMetadata.Builder clearWidth() {
      fieldSetFlags()[3] = false;
      return this;
    }

    /** Gets the value of the 'depth' field */
    public java.lang.Integer getDepth() {
      return depth;
    }
    
    /** Sets the value of the 'depth' field */
    public GeoPictureWithMetadata.Builder setDepth(int value) {
      validate(fields()[4], value);
      this.depth = value;
      fieldSetFlags()[4] = true;
      return this; 
    }
    
    /** Checks whether the 'depth' field has been set */
    public boolean hasDepth() {
      return fieldSetFlags()[4];
    }
    
    /** Clears the value of the 'depth' field */
    public GeoPictureWithMetadata.Builder clearDepth() {
      fieldSetFlags()[4] = false;
      return this;
    }

    /** Gets the value of the 'dtype' field */
    public java.lang.Integer getDtype() {
      return dtype;
    }
    
    /** Sets the value of the 'dtype' field */
    public GeoPictureWithMetadata.Builder setDtype(int value) {
      validate(fields()[5], value);
      this.dtype = value;
      fieldSetFlags()[5] = true;
      return this; 
    }
    
    /** Checks whether the 'dtype' field has been set */
    public boolean hasDtype() {
      return fieldSetFlags()[5];
    }
    
    /** Clears the value of the 'dtype' field */
    public GeoPictureWithMetadata.Builder clearDtype() {
      fieldSetFlags()[5] = false;
      return this;
    }

    /** Gets the value of the 'itemsize' field */
    public java.lang.Integer getItemsize() {
      return itemsize;
    }
    
    /** Sets the value of the 'itemsize' field */
    public GeoPictureWithMetadata.Builder setItemsize(int value) {
      validate(fields()[6], value);
      this.itemsize = value;
      fieldSetFlags()[6] = true;
      return this; 
    }
    
    /** Checks whether the 'itemsize' field has been set */
    public boolean hasItemsize() {
      return fieldSetFlags()[6];
    }
    
    /** Clears the value of the 'itemsize' field */
    public GeoPictureWithMetadata.Builder clearItemsize() {
      fieldSetFlags()[6] = false;
      return this;
    }

    /** Gets the value of the 'nbytes' field */
    public java.lang.Long getNbytes() {
      return nbytes;
    }
    
    /** Sets the value of the 'nbytes' field */
    public GeoPictureWithMetadata.Builder setNbytes(long value) {
      validate(fields()[7], value);
      this.nbytes = value;
      fieldSetFlags()[7] = true;
      return this; 
    }
    
    /** Checks whether the 'nbytes' field has been set */
    public boolean hasNbytes() {
      return fieldSetFlags()[7];
    }
    
    /** Clears the value of the 'nbytes' field */
    public GeoPictureWithMetadata.Builder clearNbytes() {
      fieldSetFlags()[7] = false;
      return this;
    }

    /** Gets the value of the 'fortran' field */
    public java.lang.Boolean getFortran() {
      return fortran;
    }
    
    /** Sets the value of the 'fortran' field */
    public GeoPictureWithMetadata.Builder setFortran(boolean value) {
      validate(fields()[8], value);
      this.fortran = value;
      fieldSetFlags()[8] = true;
      return this; 
    }
    
    /** Checks whether the 'fortran' field has been set */
    public boolean hasFortran() {
      return fieldSetFlags()[8];
    }
    
    /** Clears the value of the 'fortran' field */
    public GeoPictureWithMetadata.Builder clearFortran() {
      fieldSetFlags()[8] = false;
      return this;
    }

    /** Gets the value of the 'byteorder' field */
    public ByteOrder getByteorder() {
      return byteorder;
    }
    
    /** Sets the value of the 'byteorder' field */
    public GeoPictureWithMetadata.Builder setByteorder(ByteOrder value) {
      validate(fields()[9], value);
      this.byteorder = value;
      fieldSetFlags()[9] = true;
      return this; 
    }
    
    /** Checks whether the 'byteorder' field has been set */
    public boolean hasByteorder() {
      return fieldSetFlags()[9];
    }
    
    /** Clears the value of the 'byteorder' field */
    public GeoPictureWithMetadata.Builder clearByteorder() {
      byteorder = null;
      fieldSetFlags()[9] = false;
      return this;
    }

    /** Gets the value of the 'data' field */
    public java.util.List<ZeroSuppressed> getData() {
      return data;
    }
    
    /** Sets the value of the 'data' field */
    public GeoPictureWithMetadata.Builder setData(java.util.List<ZeroSuppressed> value) {
      validate(fields()[10], value);
      this.data = value;
      fieldSetFlags()[10] = true;
      return this; 
    }
    
    /** Checks whether the 'data' field has been set */
    public boolean hasData() {
      return fieldSetFlags()[10];
    }
    
    /** Clears the value of the 'data' field */
    public GeoPictureWithMetadata.Builder clearData() {
      data = null;
      fieldSetFlags()[10] = false;
      return this;
    }

    @Override
    public GeoPictureWithMetadata build() {
      try {
        GeoPictureWithMetadata record = new GeoPictureWithMetadata();
        record.metadata = fieldSetFlags()[0] ? this.metadata : (java.util.Map<java.lang.CharSequence,java.lang.CharSequence>) defaultValue(fields()[0]);
        record.bands = fieldSetFlags()[1] ? this.bands : (java.util.List<java.lang.CharSequence>) defaultValue(fields()[1]);
        record.height = fieldSetFlags()[2] ? this.height : (java.lang.Integer) defaultValue(fields()[2]);
        record.width = fieldSetFlags()[3] ? this.width : (java.lang.Integer) defaultValue(fields()[3]);
        record.depth = fieldSetFlags()[4] ? this.depth : (java.lang.Integer) defaultValue(fields()[4]);
        record.dtype = fieldSetFlags()[5] ? this.dtype : (java.lang.Integer) defaultValue(fields()[5]);
        record.itemsize = fieldSetFlags()[6] ? this.itemsize : (java.lang.Integer) defaultValue(fields()[6]);
        record.nbytes = fieldSetFlags()[7] ? this.nbytes : (java.lang.Long) defaultValue(fields()[7]);
        record.fortran = fieldSetFlags()[8] ? this.fortran : (java.lang.Boolean) defaultValue(fields()[8]);
        record.byteorder = fieldSetFlags()[9] ? this.byteorder : (ByteOrder) defaultValue(fields()[9]);
        record.data = fieldSetFlags()[10] ? this.data : (java.util.List<ZeroSuppressed>) defaultValue(fields()[10]);
        return record;
      } catch (Exception e) {
        throw new org.apache.avro.AvroRuntimeException(e);
      }
    }
  }
}
