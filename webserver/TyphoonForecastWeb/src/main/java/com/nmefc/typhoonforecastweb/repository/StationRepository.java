package com.nmefc.typhoonforecastweb.repository;

import com.nmefc.typhoonforecastweb.model.StationInfoEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StationRepository extends JpaRepository<StationInfoEntity, Long> {

    StationInfoEntity getById(Integer id);
}
