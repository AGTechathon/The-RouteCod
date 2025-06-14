package com.TripCraftProject.Repository;


import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.TripCraftProject.model.SnapSafari;

public interface SnapSafariRepository extends MongoRepository<SnapSafari, String> {
    List<SnapSafari> findByUserId(String userId);

}
