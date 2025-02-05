import mongoose, { SchemaTypes } from "mongoose";
const { Schema, model } = mongoose;

const BrandSchema = new mongoose.Schema({
  createdAt: Date,
  updatedAt: Date,
  name: String,
  website: String,
});

const Brand = model("Brand", BrandSchema);
export default Brand;
