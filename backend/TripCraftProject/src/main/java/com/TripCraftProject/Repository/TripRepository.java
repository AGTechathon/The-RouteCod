package com.TripCraftProject.Repository;

import java.time.LocalDate;
import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import com.TripCraftProject.model.Trip;


public interface TripRepository extends MongoRepository<Trip, String>{

	List<Trip> findByUserIdAndEndDateBefore(String userId, LocalDate date);
	List<Trip> findByUserIdAndStartDateAfter(String userId, LocalDate date);
	boolean existsByDestination(String destination);
    List<Trip> findByDestination(String destination);
   
    @Query("{ $or: [ { 'userId': ?0 }, { 'collaborators.userId': ?0 } ] }")
    List<Trip> findTripsSharedWithUser(String email);
    List<Trip> findByCollaboratorsEmail(String email);

}
