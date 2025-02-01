import mongoose from "mongoose";
import "dotenv/config";

const MONGO_URL = process.env.MONGO_URL!;

mongoose.connection.once("open", () => {
  console.log("MongoDB connection ready");
});

mongoose.connection.on("error", (err) => {
  console.log(err);
});

export const mongoConnect = async () => {
  await mongoose.connect(MONGO_URL);
};

export const mongoDisconnect = async () => {
  await mongoose.disconnect();
};
