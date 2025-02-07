import mongoose, { SchemaTypes } from "mongoose";
const { Schema, model } = mongoose;

const componentSchema = new Schema({
  createdAt: Date,
  updatedAt: Date,
  bike: { type: mongoose.Schema.Types.ObjectId, ref: "Bike" },
  component: { type: mongoose.Schema.Types.ObjectId, ref: "Component" },
});

const Component = model("Component", componentSchema);
export default Component;
