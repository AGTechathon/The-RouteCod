package com.TripCraftProject.Services;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
@Service
public class GeminiService {

    @Value("${gemini.api.url}")
    private String apiUrl;

    @Value("${gemini.api.key}")
    private String apiKey;
       private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public String buildPrompt(String destination) {
        return String.format("""
            You are a smart travel planner.

            Based only on the following destination:
            {
              "destination": "%s"
            }

            Generate a JSON response with two arrays:

            1. "spots" – Include exactly 25 unique and diverse tourist spots in and around the destination. For each spot, provide:
               - name
               - location
               - category (e.g., history, food, relaxation, adventure, nightlife, art, spiritual, nature, cultural, shopping)
               - rating (1 to 5)
               - estimatedCost (in INR)
               - timeSlot (in format "HH:MM-HH:MM")
               - longitude
               - latitude

            2. "hotels" – Include exactly 30 unique hotels near the above tourist spots:
               - 15 hotels with stayType "Stay" (for accommodation)
               - 15 hotels with stayType "Lunch" (for dining)

               For each hotel, provide:
               - name
               - location
               - category (e.g., Luxury, Budget, Casual Dining)
               - rating (1 to 5)
               - pricePerNight (in INR)
               - stayType ("Stay" or "Lunch")
               - longitude
               - latitude
               - nearbySpot (mention the closest tourist spot name)

            Guidelines:
            - All entries must be unique and relevant to the given destination.
            - Include a variety of categories and budget levels.
            - Ensure hotel locations are near the tourist spots.
            - Format output as pure valid JSON only. Example:
            {
              "spots": [ ... ],
              "hotels": [ ... ]
            }
            """, destination
        );
    }

    public String getGeminiResponse(String prompt) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("x-goog-api-key", apiKey);

        String requestBody = String.format("""
            {
              "contents": [{
                "parts": [{
                  "text": "%s"
                }]
              }]
            }
            """, prompt.replace("\"", "\\\""));

        HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(apiUrl, entity, String.class);
            String rawResponse = response.getBody();
            System.out.println("Gemini API Raw Response: " + rawResponse);

            if (response.getStatusCode().is2xxSuccessful()) {
                return extractJsonFromResponse(rawResponse);
            }
            throw new RuntimeException("API request failed: " + response.getStatusCode());
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Error calling Gemini API: " + e.getMessage());
        }
    }

    private String extractJsonFromResponse(String response) {
        try {
            JsonNode root = objectMapper.readTree(response);
            JsonNode candidates = root.path("candidates");
            if (candidates.isArray() && candidates.size() > 0) {
                JsonNode parts = candidates.get(0).path("content").path("parts");
                if (parts.isArray() && parts.size() > 0) {
                    String text = parts.get(0).path("text").asText();
                    // Clean markdown if present
                    return text
                        .replaceAll("```json\\s*", "")
                        .replaceAll("```\\s*", "")
                        .trim();
                }
            }
            throw new RuntimeException("Unexpected response structure: " + response);
        } catch (Exception e) {
            throw new RuntimeException("Error parsing response: " + e.getMessage(), e);
        }
    }

}