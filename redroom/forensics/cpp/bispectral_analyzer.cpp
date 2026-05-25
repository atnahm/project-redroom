#include "bispectral_analyzer.hpp"
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <cmath>
#include <algorithm>
#include <numeric>

namespace redroom {
namespace forensics {

BispectralAnalyzer::BispectralAnalyzer()
    : paranoid_mode_(true),
      sigma_threshold_(3.5f),
      fft_size_(512),
      biphase_threshold_(0.6f),
      gan_freq_min_(8000),
      gan_freq_max_(32000),
      diffusion_freq_min_(16000),
      diffusion_freq_max_(64000) {}

void BispectralAnalyzer::set_paranoid_mode(bool enable) {
    paranoid_mode_ = enable;
    sigma_threshold_ = enable ? 2.5f : 3.5f;
}

std::vector<std::vector<std::complex<float>>> BispectralAnalyzer::compute_1d_bispectrum(const cv::Mat& signal) {
    std::vector<std::vector<std::complex<float>>> dummy;
    return dummy;
}

float BispectralAnalyzer::compute_bicoherence(const std::vector<std::vector<std::complex<float>>>& bispectrum, int freq_band) {
    return 0.0f;
}

float BispectralAnalyzer::compute_bicoherence(const cv::Mat& phase_image) {
    cv::Scalar mean, stddev;
    cv::meanStdDev(phase_image, mean, stddev);
    float std = static_cast<float>(stddev.val[0]);
    if (std == 0.0f) return 0.0f;

    cv::Mat normalized = (phase_image - mean.val[0]) / std;
    cv::Mat squared = normalized.mul(normalized);
    cv::Mat cubed = squared.mul(normalized);

    cv::Scalar skewness = cv::mean(cubed);
    return std::min(1.0f, std::abs(static_cast<float>(skewness.val[0])) / 5.0f);
}

std::vector<float> BispectralAnalyzer::extract_radial_profile(const cv::Mat& magnitude_spectrum) {
    std::vector<float> profile;
    int cx = magnitude_spectrum.cols / 2;
    int cy = magnitude_spectrum.rows / 2;
    int max_radius = std::min(cx, cy);
    profile.resize(max_radius, 0.0f);
    std::vector<int> counts(max_radius, 0);

    for (int y = 0; y < magnitude_spectrum.rows; y++) {
        for (int x = 0; x < magnitude_spectrum.cols; x++) {
            float dx = static_cast<float>(x - cx);
            float dy = static_cast<float>(y - cy);
            int r = static_cast<int>(std::round(std::sqrt(dx*dx + dy*dy)));
            if (r < max_radius) {
                profile[r] += magnitude_spectrum.at<float>(y, x);
                counts[r]++;
            }
        }
    }

    for (int i = 0; i < max_radius; i++) {
        if (counts[i] > 0) {
            profile[i] /= counts[i];
        }
    }
    return profile;
}

cv::Mat BispectralAnalyzer::generate_heatmap(const cv::Mat& magnitude, const cv::Mat& phase) {
    cv::Mat heatmap = cv::Mat::zeros(magnitude.size(), CV_8UC3);
    return heatmap;
}

BispectralResult BispectralAnalyzer::analyze_image(const cv::Mat& image) {
    BispectralResult result;
    result.ai_probability = 0.0f;
    result.bicoherence_score = 0.0f;
    result.phase_coupling_index = 0.0f;
    result.suspected_generator = "Natural";
    result.artifact_type = "None";

    if (image.empty()) {
        result.artifact_type = "Error: Empty Image";
        return result;
    }

    cv::Mat gray;
    if (image.channels() == 3) {
        cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    } else {
        gray = image.clone();
    }

    cv::Mat padded;
    int m = cv::getOptimalDFTSize(gray.rows);
    int n = cv::getOptimalDFTSize(gray.cols);
    cv::copyMakeBorder(gray, padded, 0, m - gray.rows, 0, n - gray.cols, cv::BORDER_CONSTANT, cv::Scalar::all(0));

    cv::Mat planes[] = {cv::Mat_<float>(padded), cv::Mat::zeros(padded.size(), CV_32F)};
    cv::Mat complexI;
    cv::merge(planes, 2, complexI);

    cv::dft(complexI, complexI);

    cv::split(complexI, planes);
    cv::Mat mag, phase;
    cv::magnitude(planes[0], planes[1], mag);
    cv::phase(planes[0], planes[1], phase);

    result.bicoherence_score = compute_bicoherence(phase);

    mag += cv::Scalar::all(1);
    cv::log(mag, mag);

    mag = mag(cv::Rect(0, 0, mag.cols & -2, mag.rows & -2));
    int cx = mag.cols / 2;
    int cy = mag.rows / 2;

    cv::Mat q0(mag, cv::Rect(0, 0, cx, cy));
    cv::Mat q1(mag, cv::Rect(cx, 0, cx, cy));
    cv::Mat q2(mag, cv::Rect(0, cy, cx, cy));
    cv::Mat q3(mag, cv::Rect(cx, cy, cx, cy));

    cv::Mat tmp;
    q0.copyTo(tmp);
    q3.copyTo(q0);
    tmp.copyTo(q3);

    q1.copyTo(tmp);
    q2.copyTo(q1);
    tmp.copyTo(q2);

    cv::normalize(mag, mag, 0, 1, cv::NORM_MINMAX);
    std::vector<float> radial_profile = extract_radial_profile(mag);

    float high_freq_energy = 0.0f;
    float total_energy = 0.0f;
    int cutoff = radial_profile.size() / 2;

    for (size_t i = 0; i < radial_profile.size(); i++) {
        total_energy += radial_profile[i];
        if (i > static_cast<size_t>(cutoff)) {
            high_freq_energy += radial_profile[i];
        }
    }

    float hf_ratio = (total_energy > 0.0f) ? (high_freq_energy / total_energy) : 0.0f;
    result.phase_coupling_index = hf_ratio;

    if (result.bicoherence_score > 0.4f || hf_ratio > 0.35f) {
        result.ai_probability = std::min(1.0f, (result.bicoherence_score * 0.6f) + (hf_ratio * 0.4f) + 0.2f);

        if (result.bicoherence_score > 0.6f) {
            result.suspected_generator = "GAN (e.g., StyleGAN)";
            result.artifact_type = "Up-sampling Grid Artifacts";
        } else {
            result.suspected_generator = "Diffusion (e.g., Midjourney/DALL-E)";
            result.artifact_type = "High-Frequency Spectral Drop-off";
        }
    } else {
        result.ai_probability = std::max(0.0f, result.bicoherence_score);
    }

    result.visualization_map = generate_heatmap(mag, phase);

    return result;
}

} // namespace forensics
} // namespace redroom
