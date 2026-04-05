#include "bispectral_analyzer.hpp"
#include <opencv2/opencv.hpp>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <iostream>

namespace redroom::forensics {

BispectralAnalyzer::BispectralAnalyzer()
    : paranoid_mode_(true),
      fft_size_(512),
      biphase_threshold_(0.6f),
      gan_freq_min_(8000),
      gan_freq_max_(32000),
      diffusion_freq_min_(16000),
      diffusion_freq_max_(64000) {}

BispectralAnalysis BispectralAnalyzer::analyze(const cv::Mat& image) {
    BispectralAnalysis result;
    result.frequency_spikes.clear();
    result.anomalous_regions.clear();

    cv::Mat gray_image = image.clone();
    if (gray_image.channels() > 1) {
        cv::cvtColor(image, gray_image, cv::COLOR_BGR2GRAY);
    }

    if (gray_image.empty()) {
        result.global_bicoherence_score = 0.0f;
        result.ai_generation_probability = 0.0f;
        result.primary_artifact = "UNKNOWN";
        result.is_suspicious = false;
        return result;
    }

    gray_image.convertTo(gray_image, CV_32F);

    // Compute 2D FFT
    cv::Mat padded;
    int m = cv::getOptimalDFTSize(gray_image.rows);
    int n = cv::getOptimalDFTSize(gray_image.cols);
    cv::copyMakeBorder(gray_image, padded, 0, m - gray_image.rows, 0, n - gray_image.cols,
                       cv::BORDER_CONSTANT, cv::Scalar::all(0));

    cv::Mat planes[] = {padded, cv::Mat::zeros(padded.size(), CV_32F)};
    cv::Mat complex_image;
    cv::merge(planes, 2, complex_image);

    cv::dft(complex_image, complex_image);

    // Compute phase for bicoherence calculation
    cv::Mat phase(complex_image.size(), CV_32F);

    for (int i = 0; i < complex_image.rows; i++) {
        for (int j = 0; j < complex_image.cols; j++) {
            cv::Vec2f val = complex_image.at<cv::Vec2f>(i, j);
            phase.at<float>(i, j) = std::atan2(val[1], val[0]);
        }
    }

    // Compute bicoherence (simplified: phase consistency measure)
    float bicoherence = compute_bicoherence(phase);
    result.global_bicoherence_score = bicoherence;

    // Simple artifact classification based on bicoherence
    std::string artifact_type;
    if (bicoherence > 0.75f) {
        artifact_type = "DIFFUSION_INCOHERENCE";  // High phase jitter typical of diffusion models
    } else if (bicoherence > 0.6f) {
        artifact_type = "GAN_RINGING";  // Moderate artifacts from GANs
    } else if (bicoherence > 0.5f) {
        artifact_type = "COMPRESSION_ARTIFACT";  // Natural compression
    } else {
        artifact_type = "UNKNOWN";
    }

    result.primary_artifact = artifact_type;
    result.frequency_spikes[0] = bicoherence * 100.0f;  // Store as pseudo-frequency

    // Compute AI generation probability
    float probability = 0.0f;

    if (artifact_type == "DIFFUSION_INCOHERENCE") {
        probability = std::min(0.95f, 0.75f + (bicoherence - 0.75f) * 0.8f);
    } else if (artifact_type == "GAN_RINGING") {
        probability = std::min(0.85f, 0.60f + (bicoherence - 0.6f) * 0.8f);
    } else if (artifact_type == "COMPRESSION_ARTIFACT") {
        probability = 0.2f;
    } else {
        probability = 0.1f;
    }

    result.ai_generation_probability = probability;

    // Suspicious if above threshold
    float suspicious_threshold = paranoid_mode_ ? 0.70f : 0.60f;
    result.is_suspicious = probability > suspicious_threshold;

    return result;
}

std::vector<BispectralAnalysis> BispectralAnalyzer::analyze_frames(const std::vector<cv::Mat>& frames) {
    std::vector<BispectralAnalysis> results;

    for (const auto& frame : frames) {
        results.push_back(analyze(frame));
    }

    return results;
}

void BispectralAnalyzer::set_paranoid_mode(bool paranoid) {
    paranoid_mode_ = paranoid;
}

cv::Mat BispectralAnalyzer::get_fft_spectrum(const cv::Mat& image) {
    cv::Mat gray_image = image.clone();
    if (gray_image.channels() > 1) {
        cv::cvtColor(image, gray_image, cv::COLOR_BGR2GRAY);
    }

    gray_image.convertTo(gray_image, CV_32F);

    cv::Mat padded;
    int m = cv::getOptimalDFTSize(gray_image.rows);
    int n = cv::getOptimalDFTSize(gray_image.cols);
    cv::copyMakeBorder(gray_image, padded, 0, m - gray_image.rows, 0, n - gray_image.cols,
                       cv::BORDER_CONSTANT, cv::Scalar::all(0));

    cv::Mat planes[] = {padded, cv::Mat::zeros(padded.size(), CV_32F)};
    cv::Mat complex_image;
    cv::merge(planes, 2, complex_image);

    cv::dft(complex_image, complex_image);

    cv::Mat mag_spectrum;
    cv::magnitude(planes[0], planes[1], mag_spectrum);
    mag_spectrum += cv::Scalar::all(1);
    cv::log(mag_spectrum, mag_spectrum);

    cv::normalize(mag_spectrum, mag_spectrum, 0, 1, cv::NORM_MINMAX);

    return mag_spectrum;
}

float BispectralAnalyzer::compute_bicoherence(const cv::Mat& phase_image) {
    // Simplified bicoherence: measure of phase consistency
    // Natural images have coherent phases, deepfakes have jittery phases

    if (phase_image.empty()) return 0.0f;

    float consistency = 0.0f;
    int count = 0;

    // Sample every 10th pixel for speed
    for (int i = 10; i < phase_image.rows - 20; i += 10) {
        for (int j = 10; j < phase_image.cols - 20; j += 10) {
            float phase_curr = phase_image.at<float>(i, j);
            float phase_neighbor = phase_image.at<float>(i + 5, j + 5);

            // Phase difference (wrapped to [-π, π])
            float diff = phase_curr - phase_neighbor;
            while (diff > M_PI) diff -= 2 * M_PI;
            while (diff < -M_PI) diff += 2 * M_PI;

            // High consistency if phases are similar
            float coherence = 1.0f - (std::abs(diff) / M_PI);
            consistency += coherence;
            count++;
        }
    }

    return count > 0 ? consistency / count : 0.0f;
}

}  // namespace redroom::forensics
