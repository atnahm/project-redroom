#ifndef PRNU_EXTRACTOR_HPP
#define PRNU_EXTRACTOR_HPP

#include <opencv2/opencv.hpp>
#include <vector>
#include <map>
#include <cmath>

namespace redroom {
namespace forensics {

struct PRNUFingerprint {
    cv::Mat kernel;
    float confidence;
    int frame_count;
    std::string estimated_model;
    std::string error_message;
};

struct PRNUMatch {
    bool is_match;
    float match_score;
    std::string detected_camera;
    float spoofing_probability;
};

class PRNUExtractor {
public:
    PRNUExtractor();
    ~PRNUExtractor() = default;

    PRNUFingerprint extract_from_video(const std::string& video_path, int sample_frames = 30);
    PRNUFingerprint extract_from_image(const cv::Mat& image);
    PRNUFingerprint extract_from_frames(const std::vector<cv::Mat>& frames);

    PRNUMatch compare_to_reference(const PRNUFingerprint& observed,
                                   const std::map<std::string, cv::Mat>& reference_db);

private:
    int wiener_kernel_size_;
    int zero_mean_window_;
};

} // namespace forensics
} // namespace redroom

#endif // PRNU_EXTRACTOR_HPP
