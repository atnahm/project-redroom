#include "prnu_extractor.hpp"
#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/video/background_segm.hpp>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <iostream>

namespace redroom {
namespace forensics {

PRNUExtractor::PRNUExtractor() : wiener_kernel_size_(5), zero_mean_window_(3) {}

PRNUFingerprint PRNUExtractor::extract_from_image(const cv::Mat& image) {
    PRNUFingerprint result;
    result.frame_count = 0;
    result.confidence = 0.0f;

    if (image.empty()) {
        result.error_message = "Failed to load image";
        return result;
    }

    cv::Mat gray;
    if (image.channels() == 3) {
        cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    } else {
        gray = image.clone();
    }

    cv::Mat filtered = gray.clone();
    gray.convertTo(filtered, CV_32F);

    cv::Mat morph_kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(wiener_kernel_size_, wiener_kernel_size_));
    cv::Mat opened;
    cv::morphologyEx(filtered, opened, cv::MORPH_OPEN, morph_kernel);

    cv::Mat noise = filtered - opened;
    cv::Mat zero_mean = noise.clone();

    for (int i = zero_mean_window_; i < zero_mean.rows - zero_mean_window_; i++) {
        for (int j = zero_mean_window_; j < zero_mean.cols - zero_mean_window_; j++) {
            cv::Rect region(j - zero_mean_window_, i - zero_mean_window_, zero_mean_window_ * 2 + 1, zero_mean_window_ * 2 + 1);
            cv::Mat patch = zero_mean(region);
            float mean_val = cv::mean(patch)[0];
            patch -= mean_val;
        }
    }

    cv::Mat kernel_normalized;
    cv::normalize(zero_mean, kernel_normalized, 0, 1, cv::NORM_MINMAX);

    result.kernel = kernel_normalized;
    result.frame_count = 1;
    result.confidence = 0.75f;
    result.estimated_model = "unknown_camera";

    return result;
}

PRNUFingerprint PRNUExtractor::extract_from_video(const std::string& video_path, int sample_frames) {
    PRNUFingerprint result;
    result.frame_count = 0;
    result.confidence = 0.0f;

    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        result.error_message = "Failed to open video";
        return result;
    }

    int frame_count = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_COUNT));
    int interval = std::max(1, frame_count / sample_frames);

    cv::Mat accumulated_noise;
    bool initialized = false;

    cv::Mat frame, gray;
    int processed_frames = 0;
    int frame_idx = 0;

    while (cap.read(frame)) {
        if (frame_idx % interval == 0 && processed_frames < sample_frames) {
            if (frame.channels() == 3) {
                cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            } else {
                gray = frame.clone();
            }
            gray.convertTo(gray, CV_32F);

            if (!initialized) {
                accumulated_noise = cv::Mat::zeros(gray.rows, gray.cols, CV_32F);
                initialized = true;
            }

            cv::Mat morph_kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(wiener_kernel_size_, wiener_kernel_size_));
            cv::Mat filtered;
            cv::morphologyEx(gray, filtered, cv::MORPH_OPEN, morph_kernel);

            accumulated_noise += (gray - filtered);
            processed_frames++;
        }
        frame_idx++;
    }

    cap.release();

    if (processed_frames == 0) {
        result.error_message = "No valid frames extracted";
        return result;
    }

    accumulated_noise /= processed_frames;

    cv::Mat zero_mean = accumulated_noise.clone();
    for (int i = zero_mean_window_; i < zero_mean.rows - zero_mean_window_; i++) {
        for (int j = zero_mean_window_; j < zero_mean.cols - zero_mean_window_; j++) {
            cv::Rect region(j - zero_mean_window_, i - zero_mean_window_, zero_mean_window_ * 2 + 1, zero_mean_window_ * 2 + 1);
            cv::Mat patch = zero_mean(region);
            float mean_val = cv::mean(patch)[0];
            patch -= mean_val;
        }
    }

    cv::Mat kernel_normalized;
    cv::normalize(zero_mean, kernel_normalized, 0, 1, cv::NORM_MINMAX);

    result.kernel = kernel_normalized;
    result.frame_count = processed_frames;
    result.confidence = std::min(0.95f, 0.5f + (processed_frames / 30.0f) * 0.3f);
    result.estimated_model = "unknown_camera";

    return result;
}

PRNUFingerprint PRNUExtractor::extract_from_frames(const std::vector<cv::Mat>& frames) {
    PRNUFingerprint result;
    result.frame_count = 0;
    result.confidence = 0.0f;

    if (frames.empty()) {
        result.error_message = "No frames provided";
        return result;
    }

    cv::Mat accumulated_noise;
    bool initialized = false;

    int processed_frames = 0;

    for (const auto& frame_in : frames) {
        if (frame_in.empty()) continue;

        cv::Mat gray;
        if (frame_in.channels() == 3) {
            cv::cvtColor(frame_in, gray, cv::COLOR_BGR2GRAY);
        } else {
            gray = frame_in.clone();
        }
        gray.convertTo(gray, CV_32F);

        if (!initialized) {
            accumulated_noise = cv::Mat::zeros(gray.rows, gray.cols, CV_32F);
            initialized = true;
        }

        cv::Mat morph_kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(wiener_kernel_size_, wiener_kernel_size_));
        cv::Mat filtered;
        cv::morphologyEx(gray, filtered, cv::MORPH_OPEN, morph_kernel);

        accumulated_noise += (gray - filtered);
        processed_frames++;
    }

    if (processed_frames == 0) {
        result.error_message = "No valid frames extracted";
        return result;
    }

    accumulated_noise /= processed_frames;

    cv::Mat zero_mean = accumulated_noise.clone();
    for (int i = zero_mean_window_; i < zero_mean.rows - zero_mean_window_; i++) {
        for (int j = zero_mean_window_; j < zero_mean.cols - zero_mean_window_; j++) {
            cv::Rect region(j - zero_mean_window_, i - zero_mean_window_, zero_mean_window_ * 2 + 1, zero_mean_window_ * 2 + 1);
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

    return result;
}

PRNUMatch PRNUExtractor::compare_to_reference(const PRNUFingerprint& extracted, const std::map<std::string, cv::Mat>& reference_db) {
    PRNUMatch result;
    result.is_match = false;
    result.match_score = 0.0f;
    result.detected_camera = "unknown";
    result.spoofing_probability = 1.0f;

    if (extracted.kernel.empty() || reference_db.empty()) {
        return result;
    }

    const float MATCH_THRESHOLD = 0.85f;
    float best_score = 0.0f;
    std::string best_camera = "";

    for (const auto& pair : reference_db) {
        const std::string& camera_id = pair.first;
        const cv::Mat& ref_kernel = pair.second;

        if (extracted.kernel.size() != ref_kernel.size()) {
            continue;
        }

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
        result.spoofing_probability = std::max(0.0f, 1.0f - best_score);
    } else {
        result.is_match = false;
        result.match_score = best_score;
        result.detected_camera = "unknown";
        result.spoofing_probability = 0.8f;
    }

    return result;
}

} // namespace forensics
} // namespace redroom
