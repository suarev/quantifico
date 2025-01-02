import axios from "axios";

const fetchPlayerImage = async (playerName) => {
  const apiKey = process.env.REACT_APP_GOOGLE_API_KEY;
  const cx = process.env.REACT_APP_GOOGLE_CX;

  try {
    const response = await axios.get("https://www.googleapis.com/customsearch/v1", {
      params: {
        q: `${playerName} premier league face profile picture transparent background`, // Search query
        searchType: "image", // Image search
        imgType: "photo", // Specify photo-type images
        num: 1, // Limit to 1 result
        key: apiKey,
        cx: cx,
      },
    });

    const imageUrl = response.data.items[0]?.link; // Extract the image URL
    return imageUrl || "https://via.placeholder.com/150"; // Fallback image if none found
  } catch (error) {
    console.error("Error fetching image:", error.response?.data || error.message);
    return "https://via.placeholder.com/150"; // Fallback image on error
  }
};

export default fetchPlayerImage;
