# -*- coding: utf-8 -*-
"""生成实验二报告。"""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = r"D:\sciencemath2\实验二_基于概率生成模型的二分类_实验报告.docx"
CODE = r"D:\sciencemath2\generative_model.py"
FIG = r"D:\sciencemath2\figures"


def set_run(run, size=12, bold=False, font="宋体", ascii_font="Times New Roman", color=None):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = ascii_font
    if color is not None:
        run.font.color.rgb = RGBColor(*color)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), ascii_font)
    rFonts.set(qn("w:hAnsi"), ascii_font)
    rFonts.set(qn("w:eastAsia"), font)


def add_text(p, text, size=12, bold=False, font="宋体", ascii_font="Times New Roman"):
    run = p.add_run(text)
    set_run(run, size=size, bold=bold, font=font, ascii_font=ascii_font)
    return run


def body(doc, text, indent=True, size=12):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(4)
    pf.space_before = Pt(0)
    if indent:
        pf.first_line_indent = Cm(0.74)
    add_text(p, text, size=size)
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(12 if level == 1 else 8)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    size = 16 if level == 1 else 14
    add_text(p, text, size=size, bold=True, font="黑体", ascii_font="Times New Roman")
    return p


def formula(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    pf.left_indent = Cm(1.0)
    add_text(p, text, size=12, font="Cambria Math", ascii_font="Cambria Math")
    return p


def shade_cell(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def set_cell(cell, text, bold=False, center=True, size=10.5):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_text(p, text, size=size, bold=bold)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.autofit = True
    for j, h in enumerate(headers):
        set_cell(table.rows[0].cells[j], h, bold=True)
        shade_cell(table.rows[0].cells[j], "1F4E79")
        for run in table.rows[0].cells[j].paragraphs[0].runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            set_cell(table.rows[i + 1].cells[j], str(value), center=True)
            if i % 2 == 1:
                shade_cell(table.rows[i + 1].cells[j], "F2F2F2")
    if col_widths:
        for row in table.rows:
            for j, w in enumerate(col_widths):
                row.cells[j].width = Cm(w)
    doc.add_paragraph()
    return table


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    add_text(p, text, size=10.5, bold=True)
    return p


def add_picture(doc, path, width):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    run = p.add_run()
    run.add_picture(path, width=Cm(width))


def build():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.6)
    section.right_margin = Cm(2.6)
    section.top_margin = Cm(2.4)
    section.bottom_margin = Cm(2.4)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(0)
    add_text(title, "科学计算与数学建模", size=16, bold=True, font="黑体")

    title2 = doc.add_paragraph()
    title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title2.paragraph_format.space_before = Pt(4)
    title2.paragraph_format.space_after = Pt(10)
    add_text(title2, "实验二  基于概率生成模型的二分类", size=18, bold=True, font="黑体")

    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.paragraph_format.space_after = Pt(2)
    add_text(info, "姓名：__________    班级：__________    学号：__________", size=12)

    date = doc.add_paragraph()
    date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date.paragraph_format.space_after = Pt(8)
    add_text(date, "日期：2026年11月19日", size=12)

    heading(doc, "一、问题描述")
    body(doc, "本实验要完成一个二分类任务：根据一个人的人口普查特征，判断其年收入是否超过 5 万美元。类别 1 表示年收入大于 50K，类别 0 表示小于或等于 50K。判定规则是后验概率：若 P(C1|x) > 0.5，则把该样本判为类别 1，否则判为类别 0。")
    body(doc, "数据来自 Barry Becker 于 1994 年从人口普查数据库中抽出的记录，筛选条件为年龄大于 16 岁、调整后总收入大于 100、抽样权重大于 1、每周工作小时数大于 0。原始记录包含 14 个输入属性和 1 个收入标签：age、workclass、fnlwgt、education、education_num、marital_status、occupation、relationship、race、sex、capital_gain、capital_loss、hours_per_week、native_country、income。")
    body(doc, "实验直接使用已经整理好的特征文件。X_train 有 32561 行，X_test 有 16281 行，每行 106 维。连续属性保留原值，离散属性做了独热编码。独热之后本来会得到 107 列，其中 native_country 的 Holand-Netherlands 只出现在一侧数据中，删掉这一列后训练集和测试集对齐为 106 维。Y_train 中 0 表示 “<=50K”，1 表示 “>50K”。test.csv 不提供收入标签，需要把 16281 条预测写入 predict.csv，第一行为 id,label，之后每行是从 1 开始的编号和预测标签。")

    heading(doc, "二、设计简要描述")
    heading(doc, "2.1 数据读取与标准化", level=2)
    body(doc, "程序先读入 X_train、Y_train 和 X_test。连续特征与独热特征的数值尺度差很大，例如 fnlwgt 和 capital_gain 可达数万，而独热列只有 0 和 1。高斯分布对方差敏感，因此先用训练集的均值和标准差做标准化，并把同一组均值、标准差用到测试集：")
    formula(doc, "Z = (X − μ) / σ")
    body(doc, "μ 和 σ 只在训练集上计算。若某一列标准差为 0，则该列不缩放；本数据标准化后最小标准差约为 0.0055，没有零方差列。")

    heading(doc, "2.2 概率生成模型", level=2)
    body(doc, "假设两类条件分布都是高斯分布，并且共享同一个协方差矩阵 Σ。类别 c 的密度为")
    formula(doc, "f(x | μc, Σ) = (2π)^(−D/2) |Σ|^(−1/2) exp{ −(1/2) (x − μc)^T Σ^(−1) (x − μc) }")
    body(doc, "由贝叶斯公式，样本属于类别 1 的后验概率为")
    formula(doc, "P(C1|x) = P(x|C1)P(C1) / [ P(x|C1)P(C1) + P(x|C2)P(C2) ]")
    body(doc, "先验用样本频率估计，P(C1) = N1 / N，P(C2) = N2 / N。两类共用 Σ 时，指数里的二次项 x^T Σ^(−1) x 会消掉，后验可以写成 Sigmoid：")
    formula(doc, "P(C1|x) = σ(z)，    σ(y) = 1 / (1 + e^(−y))")
    formula(doc, "z = (μ1 − μ2)^T Σ^(−1) x − (1/2) μ1^T Σ^(−1) μ1 + (1/2) μ2^T Σ^(−1) μ2 + ln(N1 / N2)")
    body(doc, "记 w^T = (μ1 − μ2)^T Σ^(−1)，b 为上式中不含 x 的三项，则 z = w^T x + b。参数由训练集闭式求出：")
    formula(doc, "μc = (1 / Nc) Σ_{n∈c} x^n")
    formula(doc, "Σ = (1 / N) Σ_c Σ_{n∈c} (x^n − μc)(x^n − μc)^T")
    body(doc, "这里的 Σ 是类内协方差的样本量加权，分母是 N 而不是 N−1，与指导书中的平均公式一致。")
    body(doc, "独热编码会带来线性相关：同一组类别列加起来等于 1，再加上若干组之后，106 维特征的协方差不满秩。数值上 Σ 的秩是 98，最大特征值约为 3.22，另有 8 个特征值在 10^(−15) 量级，是舍入误差造成的零特征值。直接求逆不稳定，因此用 Moore-Penrose 伪逆 Σ^+ 代替 Σ^(−1)。伪逆只在非零特征值对应的子空间上求逆，丢掉这 8 个冗余方向。有效特征值与零特征值之间有明显间隙（约 0.020 对 10^(−15)），截断是明确的。")

    heading(doc, "2.3 预测与输出", level=2)
    body(doc, "对标准化后的测试样本计算 z，再经过 Sigmoid 得到 P(C1|x)。概率大于 0.5 记为 1，否则记为 0。结果写入 predict.csv。计算 Sigmoid 时把 z 限制在 [−50, 50]，避免指数溢出；这个截断只影响极端概率，不改变 0.5 阈值下的分类结果。")

    heading(doc, "2.4 程序模块", level=2)
    body(doc, "generative_model.py 按下面的顺序工作，建模和预测只用 NumPy 与 Python 标准库。matplotlib 只用来画报告中的三张图。", indent=True)
    modules = [
        "load_matrix / load_labels：读取特征矩阵和标签。",
        "standardize：用训练集统计量把训练、测试特征都变成 Z-score。",
        "fit_generative：估计 μ1、μ2、共享协方差，并用伪逆求出 w 和 b。",
        "posterior / predict_label：计算后验概率，并按 0.5 阈值给出标签。",
        "write_predict：按 id,label 写出 16281 行预测。",
        "main：串联上述步骤，并在训练集上统计准确率、混淆矩阵和类均值差。",
    ]
    for item in modules:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(1)
        add_text(p, "·  " + item, size=12)

    heading(doc, "三、程序清单")
    body(doc, "完整程序见同目录 generative_model.py，下面是带注释的源码。数据目录为桌面上的 data 文件夹，预测结果写到 D:\\sciencemath2\\predict.csv。")

    code = open(CODE, encoding="utf-8").read().replace("\t", "    ")
    for line in code.splitlines():
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        add_text(p, line if line else " ", size=8, font="Consolas", ascii_font="Consolas")

    heading(doc, "四、结果分析")
    heading(doc, "4.1 类别分布", level=2)
    body(doc, "训练集 32561 人中，年收入不超过 50K 的有 24720 人，超过 50K 的有 7841 人。类别 1 的先验只有 24.08%。如果模型把所有人都判成 0，准确率也能达到 75.92%。后面的准确率必须和这个多数类基线比较，否则 80% 左右的数字并不能说明模型有效。")
    add_picture(doc, FIG + r"\class_distribution.png", 13.5)
    caption(doc, "图 1  训练集两类人数")

    heading(doc, "4.2 训练集上的分类结果", level=2)
    body(doc, "测试集没有标签，正确性用训练集上的拟合结果检查。模型参数由全部训练样本估计，因此这是训练准确率，会略高于真正的泛化准确率，但足以判断公式和实现是否正确。")
    add_table(
        doc,
        ["", "预测 0", "预测 1", "合计"],
        [
            ["真实 0", "23005", "1715", "24720"],
            ["真实 1", "3420", "4421", "7841"],
            ["合计", "26425", "6136", "32561"],
        ],
    )
    caption(doc, "表 1  训练集混淆矩阵")
    body(doc, "判对 27426 条，训练准确率为 84.23%，比多数类基线高 8.31 个百分点。对类别 1，精确率是 4421 / 6136 = 72.05%，召回率是 4421 / 7841 = 56.38%，F1 约为 0.633。模型更少把低收入人群判成高收入，同时会漏掉将近一半真正的高收入样本。")
    body(doc, "偏置项 b = ln(N1/N2) 再加上两类均值的二次项，计算结果为 b = −1.976。负的偏置把决策边界推向类别 1，所以在 0.5 阈值下，模型预测为正类的比例低于真实先验。训练集上预测为 1 的比例是 6136 / 32561 = 18.84%。实验规定用 0.5 作为阈值，程序没有另调阈值。")
    add_picture(doc, FIG + r"\posterior_hist.png", 14.5)
    caption(doc, "图 2  训练集后验概率。虚线是 0.5 判定阈值")
    body(doc, "图 2 里，真实低收入样本大量集中在 0 附近，真实高收入样本更多地落在 0.5 右侧，但也有相当一部分留在左侧。两类直方图在 0.2 到 0.6 之间重叠，这是召回率上不去的直接原因：共享协方差的高斯假设只能给出线性边界，分不开所有重叠样本。")

    heading(doc, "4.3 哪些特征把两类分开", level=2)
    body(doc, "同一组独热列相加为 1，权重 w 在这一组内部可以同时加一个常数而不改变落在合法编码上的得分。因此单个独热权重的正负不能单独解释。更稳妥的是比较标准化之后的类均值差 μ1 − μ2：差为正，表示高收入类在该特征上更高。")
    add_picture(doc, FIG + r"\mean_gap.png", 14.5)
    caption(doc, "图 3  两类差异最大的 12 个特征")
    add_table(
        doc,
        ["更偏向高收入（μ1−μ2 > 0）", "差值", "更偏向低收入（μ1−μ2 < 0）", "差值"],
        [
            ["Married-civ-spouse", "+1.040", "Never-married", "−0.745"],
            ["Husband", "+0.938", "Own-child", "−0.534"],
            ["age", "+0.547", "Not-in-family", "−0.441"],
            ["hours_per_week", "+0.537", "Other-service", "−0.366"],
            ["capital_gain", "+0.522", "Unmarried", "−0.334"],
            ["sex（男=1，女=0）", "+0.505", "HS-grad", "−0.307"],
            ["Exec-managerial", "+0.503", "Divorced", "−0.297"],
            ["Prof-specialty", "+0.435", "Adm-clerical", "−0.210"],
        ],
    )
    caption(doc, "表 2  标准化特征上类均值差最大的属性")
    body(doc, "差别和常识一致。高收入一侧更多是已婚、丈夫、年龄更大、每周工时更长、资本利得更高、性别编码为男性，职业上则是管理人员和专业人员。低收入一侧更多是未婚、子女、不在家庭中、服务类职业和高中学历。sex 列中 Male 编码为 1、Female 编码为 0，正的均值差表示高收入类里男性比例更高。")

    heading(doc, "4.4 测试集预测", level=2)
    body(doc, "对 16281 条测试样本使用训练集的均值、标准差和同一组 w、b。预测为年收入超过 50K 的有 3010 人，占 18.49%，和训练集上 18.84% 的预测正类比例接近，说明测试集没有被标准化用错。predict.csv 共 16282 行（含表头），编号从 1 到 16281，标签只有 0 和 1。文件开头如下。")
    add_table(
        doc,
        ["id", "label"],
        [[str(i), lab] for i, lab in [
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
            (6, 0), (7, 0), (8, 1), (9, 0), (10, 0),
        ]],
        col_widths=[4, 4],
    )
    caption(doc, "表 3  predict.csv 的前 10 行预测")
    body(doc, "测试集没有公开标签，报告里不计算测试准确率。训练集 84.23% 的准确率、合理的正类比例，以及类均值差与收入常识一致，用来说明模型和输出格式是对的。")

    heading(doc, "五、调试报告")
    heading(doc, "5.1 协方差矩阵不能直接求逆", level=2)
    body(doc, "第一次按公式写 np.linalg.inv 时，协方差矩阵条件数达到 10^30 量级。原因不是编程把均值减错，而是独热编码本身不满秩：106 列里只有 98 个线性无关方向。8 个接近 0 的特征值里还有因舍入出现的负值，直接求逆会把这些方向放大成没有意义的巨大权重。")
    body(doc, "处理办法是改用伪逆。特征值从大到小排到第 98 个仍约为 0.020，第 99 个已经落到 10^(−15)，中间没有需要人为挑选的截断点。伪逆和在对角线上加一个很小的 ε 再求逆，训练准确率都在 84.2% 左右；伪逆不引入额外的 ε，和“丢掉零空间”这一事实对应，所以最终采用伪逆。")

    heading(doc, "5.2 权重的符号不能逐列解释", level=2)
    body(doc, "求出的 w 里，绝对值最大的若干维多数为负，其中 Married-civ-spouse 和 Never-married 同时为负。这两列属于同一组婚姻状况，不能一个代表高收入、一个代表低收入。检查类均值之后，Married-civ-spouse 的 μ1−μ2 为 +1.04，Never-married 为 −0.75，方向是对的。报告分析改用类均值差，避免把不可辨识的权重符号写成结论。")

    heading(doc, "5.3 类别不平衡与阈值", level=2)
    body(doc, "类别 1 只占四分之一左右，公式里的 ln(N1/N2) 自然把边界推高。结果是精确率 72%、召回率 56%。若把阈值降到 0.5 以下，召回率会上升，精确率会下降。指导书规定 P(C1|x) > 0.5 才判为类别 1，因此没有为了提高某一项指标去改阈值。")

    heading(doc, "5.4 复杂度与可以改进的地方", level=2)
    body(doc, "设样本数为 N、维数为 D。估计协方差需要把每个样本的外积加起来，时间是 O(ND^2)；求伪逆是 O(D^3)。这里 N = 32561，D = 106，一次训练在普通计算机上大约十几秒，主要时间花在读入文件和矩阵乘法。协方差矩阵只有 106×106，空间开销可以忽略。")
    body(doc, "共享协方差是这个模型能化成线性得分的条件，也是误差的主要来源。高收入和低收入人群的离散程度并不相同，尤其是 capital_gain 在高收入类里更分散。若两类各用各的协方差，决策边界不再是线性的，但 106 维下每一类的协方差更难稳定求逆。另一种改进是改用逻辑回归，直接最大化条件似然，不必假设特征服从高斯分布。本实验的要求是概率生成模型，所以上述改动只作为后续方向，没有放进提交结果。")
    body(doc, "运行方式：安装 NumPy 与 matplotlib 后，在 D:\\sciencemath2 下执行 python generative_model.py。程序读取 C:\\Users\\ROG STRIX\\Desktop\\data 中的 X_train、Y_train、X_test，生成 predict.csv、metrics.txt 和 figures 目录下的三张图。")

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    build()
