#ifndef PRNU_EXTRACTOR_HPP
#define PRNU_EXTRACTOR_HPP

#include <opencv2/opencv.hpp>
#include <vector>
#include <map>
#include <cmath>

/**
 * Photo Response Non-Uniformity (PRNU) Extractor
 * 
 * Extracts the unique "sensor fingerprint" from ingested video/image.
 * Works by analyzing residual noise patterns that are device-specific.
 * 
 * Reference: Fridrich, J., Kodovský, J. (2012). "Rich Models for Steganalysis"
 * 
 * Usage:
 *   PRNUExtractor extractor;
 *   auto fingerprint = extractor.extract_from_video("clip.mp4");
 *   float match_score = extractor.compare_to_reference(fingerprint, reference_db);
 */

struct PRNUFingerprint {
    cv::Mat kernel;              // The extracted PRNU pattern (floating point)
    float confidence;            // Confidence of extraction (0-1)
    int frame_count;             // Number of frames used
    std::string estimated_model; // e.g., "iPhone_15", "Samsung_S24"
};

struct PRNUMatch {
    bool is_match;               // True if PRNU matches known database
    float match_score;           // Cross-correlation with reference (0-1)
    std::string detected_camera; // Which camera model this PRNU belongs to
    float spoofing_probability;  // Likelihood that image is synthetic (0-1)
};

class PRNUExtractor {
public:
    PRNUExtractor();
    ~PRNUExtractor() = default;

    /**
     * Extract PRNU fingerprint from video file
     * Internally decomposes frames and isolates device-specific noise
     */
    PRNUFingerprint extract_from_video(const std::string& video_path);

    /**
     * Extract PRNU fingerprint from image (less reliable but possible)
     * Requires high-resolution image
     */
    PRNUFingerprint extract_from_image(const cv::Mat& image);

    /**
     * Extract PRNU from frame sequence with known reference
     * Better for real-time applications
     */
    PRNUFingerprint extract_from_frames(const std::vector<cv::Mat>& frames);

    /**
     * Compare extracted fingerprint against reference database
     * Reference can be pre-computed device fingerprints (iPhone, Android, etc.)
     */
    PRNUMatch compare_to_reference(const PRNUFingerprint& observed,
                                    const std::map<std::string, cv::Mat>& reference_db);

    /**
     * Load pre-built NIST camera fingerprint database
     * Can be sourced from: https://www.nist.gov/itl/iad/mig/nilsondataset
     */
    void load_reference_database(const std::string& db_path);

private:
    // Wiener filter for noise extraction
    cv::Mat extract_noise_residual(const cv::Mat& image);

    // Zero-mean normalization
    cv::Mat zero_mean_normalize(const cv::Mat& kernel);

    // Cross-correlation matching
    float compute_correlation(const cv::Mat& observed, const cv::Mat& reference);

    // Median-based camera identification
    std::string identify_camera_model(const cv::Mat& fingerprint);

    // Reference database (loaded at initialization)
    std::map<std::string, cv::Mat> reference_database;
};

#endif // PRNU_EXTRACTOR_HPP
