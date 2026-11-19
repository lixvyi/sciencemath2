# -*- coding: utf-8 -*-
"""
实验二：基于概率生成模型的二分类

任务：根据人口普查特征，判断一个人的年收入是否超过 5 万美元。
模型：两类共享协方差的高斯生成模型。后验概率经贝叶斯公式化简后
等价于对线性得分 z = w^T x + b 做 Sigmoid。

数据：
    X_train, X_test  已完成离散特征独热编码，每行 106 维
    Y_train          0 表示 <=50K，1 表示 >50K
输出：
    predict.csv      表头 id,label，id 从 1 开始，对应 test 的 16281 条记录
"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = r"C:\Users\ROG STRIX\Desktop\data"
OUT_DIR = r"D:\sciencemath2"
FIG_DIR = os.path.join(OUT_DIR, "figures")


def load_matrix(path):
    """读取带表头的数值矩阵，返回特征矩阵和列名。"""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = np.array(list(reader), dtype=float)
    return rows, [name.strip() for name in header]


def load_labels(path):
    """读取 Y_train，跳过表头。"""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        labels = np.array([int(row[0]) for row in reader], dtype=int)
    return labels


def standardize(x_train, x_test):
    """用训练集的均值和标准差做 Z-score，并作用到测试集。

    Z = (X - mu) / sigma
    标准差为 0 的列保持原值（本数据中不会出现）。
    """
    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    std_safe = std.copy()
    std_safe[std_safe == 0] = 1.0
    x_train_z = (x_train - mean) / std_safe
    x_test_z = (x_test - mean) / std_safe
    return x_train_z, x_test_z, mean, std


def fit_generative(x, y):
    """估计两类高斯的均值、共享协方差，并求出 w 与 b。

    记类别 1 为年收入 >50K，类别 2 为 <=50K。
        mu_c = (1 / N_c) * sum_{n in c} x^n
        Sigma = (1 / N) * sum_c sum_{n in c} (x^n - mu_c)(x^n - mu_c)^T

    独热编码使部分特征线性相关，Sigma 不满秩（数值秩为 98）。
    因此用 Moore-Penrose 伪逆代替公式中的逆矩阵，只在非零特征
    子空间上求逆，等价于丢掉由编码冗余造成的零特征值。

        w^T = (mu1 - mu2)^T Sigma^+
        b   = -0.5 mu1^T Sigma^+ mu1 + 0.5 mu2^T Sigma^+ mu2 + ln(N1 / N2)
        P(C1 | x) = sigmoid(w^T x + b)
    """
    x1 = x[y == 1]
    x2 = x[y == 0]
    n1 = x1.shape[0]
    n2 = x2.shape[0]
    mu1 = np.mean(x1, axis=0)
    mu2 = np.mean(x2, axis=0)

    centered1 = x1 - mu1
    centered2 = x2 - mu2
    sigma = (centered1.T @ centered1 + centered2.T @ centered2) / (n1 + n2)

    sigma_inv = np.linalg.pinv(sigma)
    diff = mu1 - mu2
    w = sigma_inv @ diff
    b = (
        -0.5 * mu1 @ sigma_inv @ mu1
        + 0.5 * mu2 @ sigma_inv @ mu2
        + np.log(n1 / n2)
    )
    return {
        "mu1": mu1,
        "mu2": mu2,
        "sigma": sigma,
        "w": w,
        "b": float(b),
        "n1": int(n1),
        "n2": int(n2),
    }


def sigmoid(z):
    """数值稳定的 Sigmoid。"""
    z = np.clip(z, -50.0, 50.0)
    return 1.0 / (1.0 + np.exp(-z))


def posterior(x, model):
    """计算每个样本属于类别 1（>50K）的后验概率。"""
    z = x @ model["w"] + model["b"]
    return sigmoid(z)


def predict_label(prob, threshold=0.5):
    """后验概率大于 0.5 判为类别 1，否则判为类别 0。"""
    return (prob > threshold).astype(int)


def confusion(y_true, y_pred):
    """返回二分类混淆矩阵的四个计数：TN, FP, FN, TP。"""
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return tn, fp, fn, tp


def write_predict(path, labels):
    """按实验要求写出 id,label。id 从 1 连续编号。"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "label"])
        for i, label in enumerate(labels, start=1):
            writer.writerow([i, int(label)])


def save_figures(y, prob, feature_names, mean_gap):
    """保存类别分布、后验直方图和两类均值差最大的特征。"""
    os.makedirs(FIG_DIR, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(6, 4))
    counts = [int(np.sum(y == 0)), int(np.sum(y == 1))]
    ax.bar(["<=50K（类别 0）", ">50K（类别 1）"], counts, color=["#4C78A8", "#F58518"])
    for i, c in enumerate(counts):
        ax.text(i, c, str(c), ha="center", va="bottom")
    ax.set_ylabel("样本数")
    ax.set_title("训练集类别分布")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "class_distribution.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.linspace(0, 1, 41)
    ax.hist(prob[y == 0], bins=bins, alpha=0.7, label="真实 <=50K", color="#4C78A8")
    ax.hist(prob[y == 1], bins=bins, alpha=0.7, label="真实 >50K", color="#F58518")
    ax.axvline(0.5, color="black", linestyle="--", linewidth=1, label="判定阈值 0.5")
    ax.set_xlabel(r"后验概率 $P(C_1\mid x)$")
    ax.set_ylabel("样本数")
    ax.set_title("训练集后验概率分布")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "posterior_hist.png"), dpi=150)
    plt.close(fig)

    order = np.argsort(mean_gap)
    picked = np.concatenate([order[:6], order[-6:]])
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [feature_names[i] for i in picked]
    values = mean_gap[picked]
    colors = ["#F58518" if v > 0 else "#4C78A8" for v in values]
    ax.barh(names, values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("标准化后的类均值差  μ1 − μ2")
    ax.set_title("两类差异最大的特征")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "mean_gap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    x_train, feature_names = load_matrix(os.path.join(DATA_DIR, "X_train"))
    x_test, test_names = load_matrix(os.path.join(DATA_DIR, "X_test"))
    y_train = load_labels(os.path.join(DATA_DIR, "Y_train"))

    if x_train.shape[1] != 106 or x_test.shape[1] != 106:
        raise ValueError("特征维数应为 106")
    if feature_names != test_names:
        raise ValueError("训练集与测试集的特征列不一致")
    if x_train.shape[0] != y_train.shape[0]:
        raise ValueError("X_train 与 Y_train 样本数不一致")

    x_train_z, x_test_z, mean, std = standardize(x_train, x_test)
    model = fit_generative(x_train_z, y_train)

    train_prob = posterior(x_train_z, model)
    train_pred = predict_label(train_prob)
    test_prob = posterior(x_test_z, model)
    test_pred = predict_label(test_prob)

    accuracy = float(np.mean(train_pred == y_train))
    tn, fp, fn, tp = confusion(y_train, train_pred)
    majority_acc = float(np.mean(y_train == 0))
    eigenvalues = np.linalg.eigvalsh(model["sigma"])
    numerical_rank = int(np.sum(eigenvalues > 1e-8))

    predict_path = os.path.join(OUT_DIR, "predict.csv")
    write_predict(predict_path, test_pred)
    mean_gap = model["mu1"] - model["mu2"]
    save_figures(y_train, train_prob, feature_names, mean_gap)

    order = np.argsort(mean_gap)
    gap_lines = [
        f"{feature_names[i]}\t{mean_gap[i]:.6f}"
        for i in np.concatenate([order[:8], order[-8:]])
    ]

    summary = [
        f"train_samples\t{x_train.shape[0]}",
        f"test_samples\t{x_test.shape[0]}",
        f"n_features\t{x_train.shape[1]}",
        f"N1_>50K\t{model['n1']}",
        f"N2_<=50K\t{model['n2']}",
        f"prior_class1\t{model['n1'] / (model['n1'] + model['n2']):.6f}",
        f"b\t{model['b']:.6f}",
        f"sigma_min_eig\t{eigenvalues[0]:.6e}",
        f"sigma_max_eig\t{eigenvalues[-1]:.6f}",
        f"sigma_rank\t{numerical_rank}",
        f"train_accuracy\t{accuracy:.6f}",
        f"majority_baseline\t{majority_acc:.6f}",
        f"TN\t{tn}",
        f"FP\t{fp}",
        f"FN\t{fn}",
        f"TP\t{tp}",
        f"precision_class1\t{tp / (tp + fp):.6f}",
        f"recall_class1\t{tp / (tp + fn):.6f}",
        f"test_predicted_positive\t{int(np.sum(test_pred == 1))}",
        f"test_positive_rate\t{float(np.mean(test_pred == 1)):.6f}",
        "mean_gap_mu1_minus_mu2",
        *gap_lines,
    ]
    summary_path = os.path.join(OUT_DIR, "metrics.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")

    print("\n".join(summary))
    print("wrote", predict_path)


if __name__ == "__main__":
    main()
