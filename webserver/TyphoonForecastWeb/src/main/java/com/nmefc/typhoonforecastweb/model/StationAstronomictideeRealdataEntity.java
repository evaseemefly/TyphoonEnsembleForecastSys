package com.nmefc.typhoonforecastweb.model;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "station_astronomictidee _realdata", schema = "typhoon_forecast_db", catalog = "")
public class StationAstronomictideeRealdataEntity {
    private int id;
    private byte isDel;
    private Timestamp gmtCreated;
    private Timestamp gmtModified;
    private String stationCode;
    private Timestamp forecastDt;
    private double surge;

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
    @Column(name = "forecast_dt", nullable = true)
    public Timestamp getForecastDt() {
        return forecastDt;
    }

    public void setForecastDt(Timestamp forecastDt) {
        this.forecastDt = forecastDt;
    }

    @Basic
    @Column(name = "surge", nullable = false, precision = 0)
    public double getSurge() {
        return surge;
    }

    public void setSurge(double surge) {
        this.surge = surge;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        StationAstronomictideeRealdataEntity that = (StationAstronomictideeRealdataEntity) o;
        return id == that.id && isDel == that.isDel && Double.compare(that.surge, surge) == 0 && Objects.equals(gmtCreated, that.gmtCreated) && Objects.equals(gmtModified, that.gmtModified) && Objects.equals(stationCode, that.stationCode) && Objects.equals(forecastDt, that.forecastDt);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, isDel, gmtCreated, gmtModified, stationCode, forecastDt, surge);
    }
}
