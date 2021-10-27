package com.nmefc.typhoonforecastweb.model;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "station_info", schema = "typhoon_forecast_db", catalog = "")
public class StationInfoEntity {
    private int id;
    private byte isDel;
    private Timestamp gmtCreated;
    private Timestamp gmtModified;
    private String name;
    private String code;
    private Double lat;
    private Double lon;
    private String desc;
    private byte isAbs;
    private int pid;

    @Id
    @Column(name = "id", nullable = false)
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    @Basic
    @Column(name = "is_del", nullable = false)
    public byte getIsDel() {
        return isDel;
    }

    public void setIsDel(byte isDel) {
        this.isDel = isDel;
    }

    @Basic
    @Column(name = "gmt_created", nullable = true)
    public Timestamp getGmtCreated() {
        return gmtCreated;
    }

    public void setGmtCreated(Timestamp gmtCreated) {
        this.gmtCreated = gmtCreated;
    }

    @Basic
    @Column(name = "gmt_modified", nullable = true)
    public Timestamp getGmtModified() {
        return gmtModified;
    }

    public void setGmtModified(Timestamp gmtModified) {
        this.gmtModified = gmtModified;
    }

    @Basic
    @Column(name = "name", nullable = false, length = 200)
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Basic
    @Column(name = "code", nullable = false, length = 50)
    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    @Basic
    @Column(name = "lat", nullable = true, precision = 0)
    public Double getLat() {
        return lat;
    }

    public void setLat(Double lat) {
        this.lat = lat;
    }

    @Basic
    @Column(name = "lon", nullable = true, precision = 0)
    public Double getLon() {
        return lon;
    }

    public void setLon(Double lon) {
        this.lon = lon;
    }

    @Basic
    @Column(name = "desc", nullable = true, length = 500)
    public String getDesc() {
        return desc;
    }

    public void setDesc(String desc) {
        this.desc = desc;
    }

    @Basic
    @Column(name = "is_abs", nullable = false)
    public byte getIsAbs() {
        return isAbs;
    }

    public void setIsAbs(byte isAbs) {
        this.isAbs = isAbs;
    }

    @Basic
    @Column(name = "pid", nullable = false)
    public int getPid() {
        return pid;
    }

    public void setPid(int pid) {
        this.pid = pid;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        StationInfoEntity that = (StationInfoEntity) o;
        return id == that.id && isDel == that.isDel && isAbs == that.isAbs && pid == that.pid && Objects.equals(gmtCreated, that.gmtCreated) && Objects.equals(gmtModified, that.gmtModified) && Objects.equals(name, that.name) && Objects.equals(code, that.code) && Objects.equals(lat, that.lat) && Objects.equals(lon, that.lon) && Objects.equals(desc, that.desc);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, isDel, gmtCreated, gmtModified, name, code, lat, lon, desc, isAbs, pid);
    }
}
