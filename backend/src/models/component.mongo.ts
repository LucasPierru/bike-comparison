import mongoose, { SchemaTypes } from "mongoose";
const { Schema, model } = mongoose;

const componentSchema = new Schema({
  createdAt: Date,
  updatedAt: Date,
  name: String,
  type: String,
  brand: { type: mongoose.Schema.Types.ObjectId, ref: "Brand" },
  currentPrice: Number,
  currency: String,
  imageUrl: String,
  source: String,
  affiliateLink: String,
});

const Component = model("Component", componentSchema);
export default Component;
