#include "prnu_extractor.hpp"
#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/video/background_segm.hpp>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <iostream>

namespace redroom::forensics {

PRNUExtractor::PRNUExtractor(int kernel_size, int zero_mean_window)
    : wiener_kernel_size_(kernel_size), zero_mean_window_(zero_mean_window) {}

PRNUFingerprint PRNUExtractor::extract_from_image(const std::string& image_path) {
    PRNUFingerprint result;

    cv::Mat image = cv::imread(image_path, cv::IMREAD_COLOR);
    if (image.empty()) {
        result.frame_count = 0;
        result.confidence = 0.0f;
        result.error_message = "Failed to load image";
        return result;
    }

    // Convert to grayscale
    cv::Mat gray;
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);

    // Extract PRNU using Wiener residual

    // Apply Wiener filter (approximated with morphological operations)
    cv::Mat filtered = gray.clone();
    gray.convertTo(filtered, CV_32F);

    // Wiener filter denoising using morphological operations
    cv::Mat morph_kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE,
                                                     cv::Size(wiener_kernel_size_, wiener_kernel_size_));
    cv::Mat opened;
    cv::morphologyEx(filtered, opened, cv::MORPH_OPEN, morph_kernel);

    cv::Mat noise = filtered - opened;  // Noise residual

    // Zero-mean normalization
    cv::Mat zero_mean = noise.clone();

    for (int i = zero_mean_window_; i < zero_mean.rows - zero_mean_window_; i++) {
        for (int j = zero_mean_window_; j < zero_mean.cols - zero_mean_window_; j++) {
            cv::Rect region(j - zero_mean_window_, i - zero_mean_window_,
                          zero_mean_window_ * 2 + 1, zero_mean_window_ * 2 + 1);
            cv::Mat patch = zero_mean(region);
            float mean_val = cv::mean(patch)[0];
            patch -= mean_val;
        }
    }

    // Normalize to [0, 1]
    cv::Mat kernel_normalized;
    cv::normalize(zero_mean, kernel_normalized, 0, 1, cv::NORM_MINMAX);

    result.kernel = kernel_normalized;
    result.frame_count = 1;
    result.confidence = 0.75f;  // Single frame = lower confidence
    result.estimated_model = "unknown_camera";
    result.error_message = "";

    return result;
}

PRNUFingerprint PRNUExtractor::extract_from_video(const std::string& video_path, int sample_frames) {
    PRNUFingerprint result;

    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        result.frame_count = 0;
        result.confidence = 0.0f;
        result.error_message = "Failed to open video";
        return result;
    }

    int frame_count = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_COUNT));
    int interval = std::max(1, frame_count / sample_frames);

    cv::Mat accumulated_noise = cv::Mat::zeros(
        static_cast<int>(cap.get(cv::CAP_PROP_FRAME_HEIGHT)),
        static_cast<int>(cap.get(cv::CAP_PROP_FRAME_WIDTH)),
        CV_32F
    );

    cv::Mat frame, gray;
    int processed_frames = 0;
    int frame_idx = 0;

    while (cap.read(frame)) {
        if (frame_idx % interval == 0 && processed_frames < sample_frames) {
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            gray.convertTo(gray, CV_32F);

            // Extract noise residual via Wiener filtering
            cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE,
                                                       cv::Size(wiener_kernel_size_, wiener_kernel_size_));
            cv::Mat filtered;
            cv::morphologyEx(gray, filtered, cv::MORPH_OPEN, kernel);

            // Accumulate noise
            accumulated_noise += (gray - filtered);
            processed_frames++;
        }
        frame_idx++;
    }

    cap.release();

    if (processed_frames == 0) {
        result.frame_count = 0;
        result.confidence = 0.0f;
        result.error_message = "No valid frames extracted";
        return result;
    }

    // Average accumulated noise
    accumulated_noise /= processed_frames;

    // Zero-mean normalization
    cv::Mat zero_mean = accumulated_noise.clone();
    for (int i = zero_mean_window_; i < zero_mean.rows - zero_mean_window_; i++) {
        for (int j = zero_mean_window_; j < zero_mean.cols - zero_mean_window_; j++) {
            cv::Rect region(j - zero_mean_window_, i - zero_mean_window_,
                          zero_mean_window_ * 2 + 1, zero_mean_window_ * 2 + 1);
            cv::Mat patch = zero_mean(region);
            float mean_val = cv::mean(patch)[0];
            patch -= mean_val;
        }
    }

    // Normalize
    cv::Mat kernel_normalized;
    cv::normalize(zero_mean, kernel_normalized, 0, 1, cv::NORM_MINMAX);

    result.kernel = kernel_normalized;
    result.frame_count = processed_frames;
    result.confidence = std::min(0.95f, 0.5f + (processed_frames / 30.0f) * 0.3f);  // 30+ frames = higher confidence
    result.estimated_model = "unknown_camera";
    result.error_message = "";

    return result;
}

PRNUFingerprint PRNUExtractor::extract_from_frames(const std::vector<std::string>& frame_paths) {
    PRNUFingerprint result;

    if (frame_paths.empty()) {
        result.frame_count = 0;
        result.confidence = 0.0f;
        result.error_message = "No frame paths provided";
        return result;
    }

    cv::Mat accumulated_noise = cv::Mat::zeros(
        cv::imread(frame_paths[0], cv::IMREAD_GRAYSCALE).rows,
        cv::imread(frame_paths[0], cv::IMREAD_GRAYSCALE).cols,
        CV_32F
    );

    int processed_frames = 0;

    for (const auto& path : frame_paths) {
        cv::Mat frame = cv::imread(path, cv::IMREAD_GRAYSCALE);
        if (frame.empty()) continue;

        frame.convertTo(frame, CV_32F);

        // Wiener filter residual
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE,
                                                   cv::Size(wiener_kernel_size_, wiener_kernel_size_));
        cv::Mat filtered;
        cv::morphologyEx(frame, filtered, cv::MORPH_OPEN, kernel);

        accumulated_noise += (frame - filtered);
        processed_frames++;
    }

    if (processed_frames == 0) {
        result.frame_count = 0;
        result.confidence = 0.0f;
        result.error_message = "No valid frames loaded";
        return result;
    }

    accumulated_noise /= processed_frames;

    // Zero-mean normalization
    cv::Mat zero_mean = accumulated_noise.clone();
    for (int i = zero_mean_window_; i < zero_mean.rows - zero_mean_window_; i++) {
        for (int j = zero_mean_window_; j < zero_mean.cols - zero_mean_window_; j++) {
            cv::Rect region(j - zero_mean_window_, i - zero_mean_window_,
                          zero_mean_window_ * 2 + 1, zero_mean_window_ * 2 + 1);
            cv::Mat patch = zero_mean(region);
            float mean_val = cv::mean(patch)[0];
            patch -= mean_val;
        }
    }

    cv::Mat kernel_normalized;
    cv::normalize(zero_mean, kernel_normalized, 0, 1, cv::NORM_MINMAX);

    result.kernel = kernel_normalized;
    result.frame_count = processed_frames;
    result.confidence = std::min(0.95f, 0.6f + (processed_frames / 30.0f) * 0.25f);
    result.estimated_model = "unknown_camera";
    result.error_message = "";

    return result;
}

PRNUMatch PRNUExtractor::compare_to_reference(const PRNUFingerprint& extracted,
                                              const std::map<std::string, cv::Mat>& reference_db) {
    PRNUMatch result;
    result.is_match = false;
    result.match_score = 0.0f;
    result.detected_camera = "unknown";
    result.spoofing_probability = 1.0f;  // Unknown = assume spoofed

    if (extracted.kernel.empty() || reference_db.empty()) {
        return result;
    }

    const float MATCH_THRESHOLD = 0.85f;
    float best_score = 0.0f;
    std::string best_camera = "";

    for (const auto& [camera_id, ref_kernel] : reference_db) {
        // Cross-correlation matching
        if (extracted.kernel.size() != ref_kernel.size()) {
            continue;  // Size mismatch
        }

        // Normalized cross-correlation
        cv::Mat corr;
        cv::matchTemplate(extracted.kernel, ref_kernel, corr, cv::TM_CCOEFF_NORMED);

        double min_val, max_val;
        cv::minMaxLoc(corr, &min_val, &max_val);

        float score = static_cast<float>(max_val);

        if (score > best_score) {
            best_score = score;
            best_camera = camera_id;
        }
    }

    if (best_score > MATCH_THRESHOLD) {
        result.is_match = true;
        result.match_score = best_score;
        result.detected_camera = best_camera;
        result.spoofing_probability = 1.0f - best_score;  // Higher match = lower spoofing prob
    } else {
        result.is_match = false;
        result.match_score = best_score;
        result.detected_camera = "unknown";
        result.spoofing_probability = 0.8f;  // Unknown camera = suspicious
    }

    return result;
}

}  // namespace redroom::forensics
