import mongoose, { SchemaTypes } from 'mongoose';
const { Schema, model } = mongoose;

const componentSchema = new Schema({
  createdAt: Date,
  updatedAt: Date,
  name: String,
  type: String,
  sizes: [String],
  brand: { type: Schema.Types.ObjectId, ref: 'Brand' },
  source: String,
  affiliateLink: String
});

const Component = model('Component', componentSchema);
export default Component;
