import mongoose, { SchemaTypes } from "mongoose";
const { Schema, model } = mongoose;

const bikeSchema = new Schema({
  createdAt: Date,
  updatedAt: Date,
  name: String,
  description: String,
  brand: { type: mongoose.Schema.Types.ObjectId, ref: "Brand" },
  currentPrice: Number,
  currency: String,
  imageUrl: String,
  source: String,
  affiliateLink: String,
  weight: String,
  weightLimit: String,
  variations: [
    {
      color: String,
      sizes: [String],
    },
  ],
  components: [
    {
      type: String,
      value: { type: mongoose.Schema.Types.ObjectId, ref: "Component" },
    },
  ],
});

const Bike = model("Bike", bikeSchema);
export default Bike;
