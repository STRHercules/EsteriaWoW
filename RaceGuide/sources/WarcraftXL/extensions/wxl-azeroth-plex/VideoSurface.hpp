#pragma once

#include "wxl/EventScript.hpp"
#include "VideoShared.hpp"

#include <windows.h>

#include <cstdint>
#include <string>
#include <vector>

struct IDirect3DDevice9;
struct IDirect3DTexture9;

namespace wxl_video_screen
{
    class VideoSurface final : public wxl::ext::EventScript
    {
    public:
        static VideoSurface& Instance();

        bool Initialize(const WXL_Api* api);
        void DrawPanel();

    private:
        VideoSurface();

        using SceneClearFn = void(__cdecl*)(uint32_t flags, uint32_t colour);
        static void __cdecl SceneClearHook(uint32_t flags, uint32_t colour);

        void OnFrame(const wxl::events::FrameArgs& args);
        void OnWorldSceneEnd(const wxl::events::WorldSceneEndArgs& args);
        void OnInput(const wxl::events::InputArgs& args);
        void OnUpdate(const wxl::events::UpdateArgs& args);
        void OnDeviceLost(const wxl::events::DeviceResetArgs& args);
        void OnDeviceReset(const wxl::events::DeviceResetArgs& args);
        void OnWorldLeave(const wxl::events::WorldLeaveArgs& args);

        void DrawPlexPanel();
        void DrawPlexLogin();
        void DrawPlexServers();
        void DrawPlexHome();
        void DrawPlexLibrary();
        void DrawPlexSearch();
        void DrawPlexDetails();
        void DrawPlexPlayer();
        void DrawPlexParty();
        void DrawPlexQueue();
        void DrawPlexSettings();
        void DrawMiniPlayer();
        bool OpenHost();
        void HideHost();
        void CloseHost();
        bool PlaceInFront();
        void Rotate(float degrees);
        void SavePlacement();
        void LoadPlacement();
        void SaveUiPreferences();
        void LoadUiPreferences();
        void LoadCinemaPresets();
        void SaveCinemaPresets();
        void ApplyCinemaPreset(size_t index);
        void SaveCurrentCinemaPreset();
        void ApplySharedCinema();
        void ShareCurrentCinema();
        float ScreenAspectRatio() const;
        void VideoLayout(float targetHalfWidth, float targetHalfHeight,
                         float& videoHalfWidth, float& videoHalfHeight,
                         float& u0, float& v0, float& u1, float& v1) const;

        bool ConnectFrames();
        bool ConnectControl();
        bool ConnectUi();
        bool SendCommand(LONG command);
        bool SendUiCommand(wxl_video_shared::UiCommand command, LONG index = -1,
                           LONG value = 0, const char* text = nullptr);
        bool RefreshUiState();
        void SendVolume(int volume);
        bool ValidateFrames() const;
        bool UploadLatestFrame(IDirect3DDevice9* device);
        void ReleaseTexture();
        void DrawWorldScreen(IDirect3DDevice9* device, void* sceneDepth, bool beforeWorld);
        void DrawPinnedScreen(IDirect3DDevice9* device);
        bool GetPinnedRect(IDirect3DDevice9* device, float& left, float& top,
                           float& right, float& bottom) const;
        std::wstring ExtensionDirectory() const;

        const WXL_Api* api_ = nullptr;
        HANDLE mapping_ = nullptr;
        void* mappingView_ = nullptr;
        HANDLE controlMapping_ = nullptr;
        void* controlView_ = nullptr;
        HANDLE uiMapping_ = nullptr;
        void* uiView_ = nullptr;
        wxl_video_shared::UiSnapshot uiState_{};
        char search_[wxl_video_shared::kUiTextBytes]{};
        char partyCode_[32]{};
        float scrubPositionSeconds_ = 0.0f;
        DWORD lastScrubAt_ = 0;
        bool plexPanelOpen_ = false;
        int miniPlayerEnabled_ = 1;
        DWORD lastConnectAttempt_ = 0;
        LONG lastFrameSequence_ = 0;
        LONG lastDrawResult_ = static_cast<LONG>(0x8000000AL);
        LONG lastStateResult_ = 0;
        uint64_t worldSceneCalls_ = 0;
        uint64_t drawAttempts_ = 0;
        uint64_t drawSuccesses_ = 0;
        DWORD lastDrawFailureLog_ = 0;
        bool loggedFirstWorldScene_ = false;
        bool preWorldDrawn_ = false;
        bool projectedCenterValid_ = false;
        float projectedCenter_[3]{};
        float projectedClipW_ = 0.0f;
        IDirect3DDevice9* textureDevice_ = nullptr;
        IDirect3DTexture9* texture_ = nullptr;
        std::vector<uint8_t> frameScratch_;

        bool initialized_ = false;
        bool placed_ = false;
        int visible_ = 1;
        int depthTest_ = 1;
        int outline_ = 0;
        float depthBias_ = -0.010f;
        int spatialAudio_ = 1;
        int masterVolume_ = 80;
        int effectiveVolume_ = 80;
        int lastSentVolume_ = -1;
        uint32_t lastVolumeUpdate_ = 0;
        int mapId_ = -1;
        float center_[3]{};
        float right_[3]{ 0.0f, 1.0f, 0.0f };
        float width_ = 8.0f;
        float screenRotationDegrees_ = 0.0f;
        float placeDistance_ = 10.0f;
        float bottomOffset_ = 0.5f;
        float fullVolumeDistance_ = 6.0f;
        float silentDistance_ = 60.0f;
        int pinned_ = 0;
        float pinnedLeft_ = 0.64f;
        float pinnedTop_ = 0.04f;
        float pinnedWidth_ = 0.32f;
        bool pinnedDragging_ = false;
        bool pinnedResizing_ = false;
        float pinnedDragOffsetX_ = 0.0f;
        float pinnedDragOffsetY_ = 0.0f;
        struct CinemaPreset
        {
            std::string name;
            float width = 8.0f;
            float bottomOffset = 0.5f;
            float rotationDegrees = 0.0f;
            int pinned = 0;
            float pinnedLeft = 0.64f;
            float pinnedTop = 0.04f;
            float pinnedWidth = 0.32f;
            int depthTest = 1;
            float depthBias = -0.010f;
            int spatialAudio = 1;
            float silentDistance = 60.0f;
            int aspectRatioMode = 0;
            int fitMode = 0;
            int frameStyle = 0;
            int ambientLighting = 0;
            bool builtIn = false;
        };

        std::vector<CinemaPreset> cinemaPresets_;
        char cinemaPresetName_[64]{"Custom Cinema"};
        int selectedCinemaPreset_ = 0;
        int aspectRatioMode_ = 0;
        int fitMode_ = 0;
        int frameStyle_ = 0;
        int ambientLighting_ = 0;
        int cinemaMode_ = 0;
        uint32_t ambientColor_ = 0xFF202020u;
        DWORD lastAmbientSampleAt_ = 0;
        std::string lastSharedCinemaSignature_;
        std::string status_ = "Waiting for the cinema helper.";

        static SceneClearFn originalSceneClear_;
    };
}
