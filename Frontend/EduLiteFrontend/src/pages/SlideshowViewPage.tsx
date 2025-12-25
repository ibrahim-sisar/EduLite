import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import { SlideshowViewer } from "../components/slideshow";

const SlideshowViewPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    // Validate that id is a valid number
    if (!id || isNaN(Number(id))) {
      toast.error(t("slideshow.view.invalidId"));
      navigate("/slideshows", { replace: true });
    }
  }, [id, navigate, t]);

  const handleExit = () => {
    navigate(`/slideshows/${id}`);
  };

  // If id is invalid, don't render the viewer (useEffect will redirect)
  if (!id || isNaN(Number(id))) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-gray-900">
      <SlideshowViewer
        slideshowId={Number(id)}
        onExit={handleExit}
        allowFullscreen={true}
      />
    </div>
  );
};

export default SlideshowViewPage;
