# AWS Cybersecurity Threat Detection: Machine Learning at Scale

## Overview

This project demonstrates a **production-ready machine learning pipeline** for detecting cybersecurity threats in network traffic using Amazon SageMaker. By leveraging XGBoost classification and AWS's managed ML services, we build a scalable system that identifies suspicious network events in real-time with high accuracy.

The solution automates the complete ML lifecycle: from data preprocessing through model training, validation, and deployment—all orchestrated through SageMaker Pipelines.

---

## 🎯 Project Goals

- **Detect network anomalies** that indicate potential security threats
- **Automate ML workflows** to reduce manual intervention
- **Scale predictions** with a production-ready SageMaker endpoint
- **Maintain audit trails** of all model versions and deployments
- **Enable real-time threat classification** for incoming network events

---

## 🏗️ Architecture

```
Raw Network Logs (S3)
        ↓
   [Preprocessing]
   (preprocess.py)
        ↓
   Train/Validation Split
        ↓
   [SageMaker Pipeline]
   - Preprocessing Step
   - Training Step (XGBoost)
   - Model Registry Step
        ↓
   Model Package Group
   ("ThreatDetectionModels")
        ↓
   [SageMaker Endpoint]
   (Real-time Inference)
        ↓
   Threat Score + Classification
```

### Components

| Component | Purpose |
|-----------|---------|
| **SageMaker Processing** | Scales data preprocessing across distributed instances |
| **XGBoost Training** | Binary classification model (Suspicious vs Normal) |
| **Model Registry** | Version control and approval workflow for models |
| **SageMaker Endpoint** | REST API for real-time threat detection |
| **CloudWatch Logs** | Monitor pipeline execution and endpoint metrics |

---

## 📊 Dataset Features

The threat detection model analyzes **11 network event features**:

| Feature | Description | Example |
|---------|-------------|---------|
| `src_ip_int` | Source IP as integer | 167772160 |
| `dst_ip_int` | Destination IP as integer | 134744072 |
| `src_port` | Source port number | 54321 |
| `dst_port` | Destination port number | 443 |
| `protocol` | Network protocol (0=TCP, 1=UDP, etc.) | 0 |
| `bytes_sent` | Upload bytes | 15000 |
| `bytes_recv` | Download bytes | 3200 |
| `duration_ms` | Connection duration | 120 |
| `packet_count` | Total packets exchanged | 45 |
| `flag` | TCP flags indicator | 1 |
| `byte_ratio` | Ratio of sent/received bytes | 4.69 |

**Target Variable**: `label` (1 = Suspicious, 0 = Normal)

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate IAM permissions
- Python 3.8+
- AWS CLI configured with credentials
- Jupyter environment (SageMaker Studio or local)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nishchal-Panta/AWS-Cybersecurity_threat_detection.git
   cd AWS-Cybersecurity_threat_detection
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file (add to .gitignore)
   echo "AWS_ACCOUNT_ID=<your-12-digit-account-id>" > .env
   echo "AWS_REGION=us-east-1" >> .env
   ```

3. **Configure IAM Role**
   
   Create an IAM role `ThreatDetectionSageMakerRole` with permissions for:
   - S3 bucket access (read/write)
   - SageMaker full access
   - CloudWatch Logs
   
   Apply the provided policy: `Inline_Policy-Glue_AND_Athena.json`

---

## 📋 File Structure

```
AWS-cybersecurity_threat_detection/
├── README.md                              # Project documentation
├── pipeline.ipynb                         # SageMaker Pipeline definition
├── endpoint.ipynb                         # Endpoint deployment & testing
├── preprocess.py                          # Data preprocessing logic
├── Inline_Policy-Glue_AND_Athena.json    # IAM policy template
└── .env                                   # Environment variables (git-ignored)
```

### File Descriptions

#### `pipeline.ipynb`
**Purpose**: Orchestrates the complete ML workflow

**Key Steps**:
1. **Preprocessing**: Cleans data, removes NaN values, reorders columns (label first)
2. **Train/Validation Split**: 80/20 stratified split ensuring class balance
3. **XGBoost Training**: Binary classification with tuned hyperparameters
4. **Model Registration**: Auto-approves model and adds to registry

**Hyperparameters**:
```python
{
    "objective": "binary:logistic",      # Binary classification
    "num_round": "200",                   # 200 boosting rounds
    "max_depth": "6",                     # Tree depth limit
    "eta": "0.2",                         # Learning rate
    "subsample": "0.8",                   # Row subsampling
    "colsample_bytree": "0.8",           # Feature subsampling
    "eval_metric": "auc",                 # Evaluation metric
    "scale_pos_weight": "10"              # Handle class imbalance
}
```

#### `endpoint.ipynb`
**Purpose**: Deploys the model and tests real-time inference

**Workflow**:
1. Retrieves the latest approved model from registry
2. Deploys to `ml.m5.large` instance with CSV serialization
3. Invokes endpoint with sample network event
4. Returns threat score (0-1) and classification

**Sample Prediction**:
```python
Input: "167772160,134744072,54321,443,0,15000,3200,120,45,1,4.69"
Output: 
  Threat score: 0.9660
  Classification: SUSPICIOUS
```

#### `preprocess.py`
**Purpose**: Handles data preprocessing in SageMaker Processing job

**Operations**:
- Concatenates CSV files from S3
- Removes rows with missing values
- Reorders columns (label first for XGBoost)
- Stratified train/val split (80/20)
- Outputs CSV files without headers

**I/O**:
- **Input**: `/opt/ml/processing/input/*.csv`
- **Output**: 
  - Train: `/opt/ml/processing/output/train/train.csv`
  - Validation: `/opt/ml/processing/output/validation/validation.csv`

---

## 🔄 Execution Steps

### Step 1: Run the Training Pipeline

Open `pipeline.ipynb` in SageMaker Studio:

```python
# Load environment variables
import os
ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
REGION = os.getenv("AWS_REGION", "us-east-1")

# Execute pipeline
pipeline.upsert(role_arn=ROLE_ARN)
execution = pipeline.start()
execution.wait()
print("Pipeline complete. Model registered.")
```

**Expected Output**:
- ✅ Preprocessing job completes
- ✅ Training job trains for ~10-15 minutes
- ✅ Model registered with "Approved" status
- ✅ Ready for deployment

### Step 2: Deploy the Endpoint

Open `endpoint.ipynb`:

```python
# Deploy latest approved model
predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name="threat-detection-endpoint"
)
print(f"Endpoint live: {predictor.endpoint_name}")
```

**Expected Output**:
```
Endpoint live: threat-detection-endpoint
```

### Step 3: Test with Sample Data

```python
# Invoke endpoint with network event
response = runtime.invoke_endpoint(
    EndpointName="threat-detection-endpoint",
    ContentType="text/csv",
    Body="167772160,134744072,54321,443,0,15000,3200,120,45,1,4.69"
)

score = float(response["Body"].read().decode("utf-8"))
label = "SUSPICIOUS" if score >= 0.5 else "NORMAL"
print(f"Threat score: {score:.4f}")
print(f"Classification: {label}")
```

---

## 📈 Model Performance

**XGBoost Configuration Rationale**:

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| `objective` | `binary:logistic` | Binary threat classification |
| `scale_pos_weight` | `10` | Account for threat class imbalance |
| `max_depth` | `6` | Prevent overfitting on sparse threat patterns |
| `subsample` | `0.8` | Reduce variance with row subsampling |
| `eta` | `0.2` | Moderate learning rate for stability |
| `eval_metric` | `auc` | Focus on ranking quality (ROC-AUC) |

**Expected Metrics**:
- AUC: 0.92+
- Precision: 0.88+
- Recall: 0.85+

---

## 🔐 Security Best Practices

### Implemented

✅ **Environment Variables**: AWS Account ID and Region stored in `.env` (git-ignored)

✅ **IAM Roles**: Least-privilege role for SageMaker operations

✅ **Endpoint Access**: VPC security groups restrict access

✅ **Audit Trail**: Model registry tracks all versions and approvals

### Recommendations

- 🔒 **Enable S3 encryption** at rest (SSE-S3 or KMS)
- 🔒 **Use VPC endpoints** for private S3/SageMaker communication
- 🔒 **Enable CloudTrail** for API audit logs
- 🔒 **Rotate credentials** regularly
- 🔒 **Monitor endpoint** for unusual prediction patterns

---

## 💰 Cost Optimization

### Estimated Monthly Costs

| Resource | Instance | Duration | Cost |
|----------|----------|----------|------|
| Processing Job | ml.t3.medium (1) | ~5 min | ~$0.05 |
| Training Job | ml.m5.xlarge (1) | ~15 min | ~$0.50 |
| Endpoint | ml.m5.large (1) | 24/7 | ~$50 |
| **Total** | - | - | **~$50/month** |

### Cost Reduction Tips

- Use **Spot Instances** for training (up to 70% savings)
- **Scale endpoint down** during low-traffic periods
- **Batch inference** if real-time requirements allow
- **Auto-scaling** based on CloudWatch metrics

---

## 🔍 Monitoring & Troubleshooting

### CloudWatch Metrics

Monitor these in CloudWatch dashboard:

```
/aws/sagemaker/Endpoints/threat-detection-endpoint
├── ModelLatency          # Prediction latency (ms)
├── ModelInvocations     # Inference count
├── ModelInvocation4XXErrors
└── ModelInvocation5XXErrors
```

### Common Issues

**Issue**: `ModelPackageArn` not found
- **Solution**: Ensure pipeline executed successfully and model was approved

**Issue**: Endpoint in-service but predictions timeout
- **Solution**: Check S3 bucket accessibility and VPC configuration

**Issue**: Poor model performance
- **Solution**: Review training logs, increase `max_depth`, collect more threat labels

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📚 References

- [AWS SageMaker Pipelines Documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html)
- [XGBoost Algorithm in SageMaker](https://docs.aws.amazon.com/sagemaker/latest/dg/xgboost.html)
- [SageMaker Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 📞 Contact & Support

**Author**: Nishchal Panta

**Repository**: [GitHub - AWS-Cybersecurity_threat_detection](https://github.com/Nishchal-Panta/AWS-Cybersecurity_threat_detection)

For issues, questions, or suggestions, please open a GitHub Issue or contact the maintainer.

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- AWS SageMaker team for excellent ML infrastructure
- XGBoost community for the powerful gradient boosting library
- Cybersecurity research community for threat detection methodologies

---

**Last Updated**: May 2026  
**Status**: Production Ready ✅
