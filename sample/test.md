# Workload-Aware Anonymization

Kristen LeFevre $^{1} \quad$ David J. DeWitt ${ }^{1} \quad$ Raghu Ramakrishnan ${ }^{1,2}$<br>${ }^{1}$ University of Wisconsin - Madison, 1210 West Dayton St., Madison, WI 53706<br>${ }^{2}$ Yahoo! Research, 701 First Ave., Sunnyvale, CA 94089


#### Abstract

Protecting data privacy is an important problem in microdata distribution. Anonymization algorithms typically aim to protect individual privacy, with minimal impact on the quality of the resulting data. While the bulk of previous work has measured quality through one-size-fits-all measures, we argue that quality is best judged with respect to the workload for which the data will ultimately be used.

This paper provides a suite of anonymization algorithms that produce an anonymous view based on a target class of workloads, consisting of one or more data mining tasks, as well as selection predicates. An extensive experimental evaluation indicates that this approach is often more effective than previous anonymization techniques.


### Single Target Classification Model

The Mondrian algorithm was recently proposed for kanonymization using multidimensional recoding [17]. The algorithm is based on a greedy recursive partitioning of the (multidimensional) quasi-identifier domain space (see Figure 3). In order to obtain approximately uniform partition occupancy, [17] suggests recursively choosing the split attribute with the largest normalized range of values, and (for continuous or ordinal attributes) partitioning the data around the median value of the split attribute. This process is repeated until no allowable split remains, meaning that a particular region cannot be further divided without violating the anonymity constraint, or constraints imposed by value generalization hierarchies. We refer to this algorithm as Median Mondrian.

When the (set of) target mining model(s) is known, we can improve this heuristic. First consider a single target classification model, with predictor attributes $Q_{1}, \ldots, Q_{d}$ (also the quasi-identifier) and class label $C$. In this case, we propose a heuristic partitioning scheme based on information gain, which is reminiscent of decision tree construction. Intuitively, the goal of this greedy criterion is to produce homogeneous partitions of class labels.

At each recursive step, we choose the split that minimizes the weighted entropy over the set of resulting partitions (without violating the anonymity constraint). $P$ denotes the current (recursive) tuple set, and partitions $P^{\prime}$ denotes the set of partitions resulting from the candidate split. $p\left(c \mid P^{\prime}\right)$ is the fraction of tuples in $P^{\prime}$ with class label $C=c$. We refer to this algorithm as InfoGain Mondrian.

$$
\operatorname{Entropy}(P, C)=\sum_{\text {partitions } P^{\prime}} \frac{\left|P^{\prime}\right|}{|P|} \sum_{c \in D_{C}}-p\left(c \mid P^{\prime}\right) \log p\left(c \mid P^{\prime}\right)
$$

InfoGain Mondrian handles continuous quasi-identifier values as they are typically handled by decision-trees, partitioning around the threshold value with smallest entropy (see [12]). The data is first sorted with respect to the split attribute. Then the data is scanned, and each time there is a change in class label, this candidate threshold is checked with respect to anonymity and entropy. In the event that no candidate threshold satisfies the anonymity constraint, the median is also checked as a default

InfoGain Mondrian scales to large data sets through a straightforward adaptation of an existing scalable decisiontree induction scheme, such as RainForest [14].
