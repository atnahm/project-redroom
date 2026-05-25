#ifndef BISPECTRAL_ANALYZER_HPP
#define BISPECTRAL_ANALYZER_HPP

#include <opencv2/opencv.hpp>
#include <vector>
#include <complex>

namespace redroom {
namespace forensics {

struct BispectralResult {
    float ai_probability;
    float bicoherence_score;
    float phase_coupling_index;
    std::string suspected_generator;
    std::string artifact_type;
    cv::Mat visualization_map;
};

class BispectralAnalyzer {
public:
    BispectralAnalyzer();
    ~BispectralAnalyzer() = default;

    BispectralResult analyze_image(const cv::Mat& image);

    void set_paranoid_mode(bool enable);

private:
    bool paranoid_mode_;
    float sigma_threshold_;
    int fft_size_;
    float biphase_threshold_;

    int gan_freq_min_;
    int gan_freq_max_;
    int diffusion_freq_min_;
    int diffusion_freq_max_;

    std::vector<std::vector<std::complex<float>>> compute_1d_bispectrum(const cv::Mat& signal);
    float compute_bicoherence(const std::vector<std::vector<std::complex<float>>>& bispectrum, int freq_band);
    float compute_bicoherence(const cv::Mat& phase_image);
    std::vector<float> extract_radial_profile(const cv::Mat& magnitude_spectrum);
    cv::Mat generate_heatmap(const cv::Mat& magnitude, const cv::Mat& phase);
};

} // namespace forensics
} // namespace redroom

#endif // BISPECTRAL_ANALYZER_HPP
