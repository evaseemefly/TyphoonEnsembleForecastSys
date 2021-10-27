package com.nmefc.typhoonforecastweb.model;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "station_stationalerttidemodel", schema = "typhoon_forecast_db", catalog = "")
public class StationStationalerttidemodelEntity {
    private int id;
    private byte isDel;
    private Timestamp gmtCreated;
    private Timestamp gmtModified;
    private String stationCode;
    private double tide;
    private int alert;

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
    @Column(name = "station_code", nullable = false, length = 10)
    public String getStationCode() {
        return stationCode;
    }

    public void setStationCode(String stationCode) {
        this.stationCode = stationCode;
    }

    @Basic
    @Column(name = "tide", nullable = false, precision = 0)
    public double getTide() {
        return tide;
    }

    public void setTide(double tide) {
        this.tide = tide;
    }

    @Basic
    @Column(name = "alert", nullable = false)
    public int getAlert() {
        return alert;
    }

    public void setAlert(int alert) {
        this.alert = alert;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        StationStationalerttidemodelEntity that = (StationStationalerttidemodelEntity) o;
        return id == that.id && isDel == that.isDel && Double.compare(that.tide, tide) == 0 && alert == that.alert && Objects.equals(gmtCreated, that.gmtCreated) && Objects.equals(gmtModified, that.gmtModified) && Objects.equals(stationCode, that.stationCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, isDel, gmtCreated, gmtModified, stationCode, tide, alert);
    }
}
