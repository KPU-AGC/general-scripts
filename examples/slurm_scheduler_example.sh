#!/bin/bash
## run as: sbatch *.sh

## SBATCH VARIABLES
#SBATCH --cpus-per-task=32
#SBATCH --mem=128000M
#SBATCH --time=01:00:00
#SBATCH --account=def-padams
#SBATCH --job-name=qiime2_pipeline_test
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.error
#SBATCH --mail-user=erick.samera@kpu.ca
#SBATCH --mail-type=ALL

## VARIABLES
QIIME2_PATH=~/singularity/qiime2-2022.2.sif
##SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
##PROJECT_PATH=$(dirname $SCRIPT_PATH)
PROJECT_PATH=~/projects/def-padams/ericksam/ion-torrent-protocols
RUNTIME=$(date +'%Y%m%d-%H%M')
LOGFILE=$PROJECT_PATH/outputs/$RUNTIME/$RUNTIME.log

## MAKE A DIRECTORY FOR THE OUTPUT
mkdir -p $PROJECT_PATH/outputs/$RUNTIME

echo "[`date`]: Starting job ..." >> $LOGFILE

## LOAD SINGULARITY
module load singularity

## IMPORT FASTQs AS QIIME2 ARTIFACTS
## The IonTorrent should've already trimmed the adapters + barcodes + primers.
## The FASTQ data should also be set up in single reads.
## A manifest file is then therefore required. Check this out on.
echo "[`date`]: Importing FASTQ as QIIME artifacts ..." >> $LOGFILE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime tools import \
    --type 'SampleData[SequencesWithQuality]' \
    --input-path /data/manifest.tsv \
    --output-path /outputs/reads_trimmed.qza \
    --input-format SingleEndFastqManifestPhred33V2 \
    >> $LOGFILE

## SUMMARIZE FASTQs
## This is useful for visualizing the quality scores of the imported dataset.
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime demux summarize \
    --i-data /outputs/reads_trimmed.qza \
    --o-visualization /outputs/reads_trimmed_stats.qzv \
    >> $LOGFILE
echo "[`date`]: Completed -- Importing FASTQ as QIIME artifacts ." >> $LOGFILE


## FILTER OUT LOW-QUALITY READS
## This uses the default options for filtering out low-quality reads.
## There's documentation saying that IonTorrent data tends to be a little lower quality compared to
## Illumina data, so make sue to visualize the filtered reads as well.
echo "[`date`]: Filtering out low-quality reads ..." >> $LOGFILE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime quality-filter q-score \
   --i-demux /outputs/reads_trimmed.qza \
   --o-filter-stats /outputs/filt_stats.qza \
   --o-filtered-sequences /outputs/reads_trimmed_filt.qza \
   >> $LOGFILE

singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime demux summarize \
    --i-data /outputs/reads_trimmed_filt.qza \
    --o-visualization /outputs/reads_trimmed_filt_summary.qzv \
    >> $LOGFILE
echo "[`date`]: Completed -- Filtering out low-quality reads ..." >> $LOGFILE

## RUNNING DADA2
## Most pipelines either use deblur or DADA2 to denoise the reads. The Langille Lab at Dal, along
## with many other forum sources, has done in-house testing which determines this to be the better
## option when dealing with IonTorrent data.
# --p-trim-left 15 is recommended for IonTorrent
echo "[`date`]: Denoising reads with DADA2 ..." >> $LOGFILE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime dada2 denoise-single \
    --verbose \
   --i-demultiplexed-seqs /outputs/reads_trimmed_filt.qza \
   --p-trunc-len 0 \
   --p-trim-left 15 \
   --p-max-ee 3 \
   --output-dir /outputs/dada2_output \
    >> $LOGFILE

## SUMMARIZING DADA2 OUTPUT
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime feature-table summarize \
    --i-table /outputs/dada2_output/table.qza \
    --o-visualization /outputs/dada2_output/dada2_table_summary.qzv \
    >> $LOGFILE

## READ COUNT TABLE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime tools export \
    --input-path /outputs/dada2_output/denoising_stats.qza \
    --output-path /outputs/dada2_output \
    >> $LOGFILE

mv \
    $PROJECT_PATH/outputs/$RUNTIME/dada2_output/stats.tsv \
    $PROJECT_PATH/outputs/$RUNTIME/dada2_output/dada2_stats.tsv \
    >> $LOGFILE
echo "[`date`]: Completed -- Denoising reads with DADA2 ..." >> $LOGFILE

## ASSIGN TAXONOMY TO ASVs
## The VSEARCH classifier is used here to deal with the fact that IonTorrent produces reads that 
## are not necessarily organized in Forward reads then Reverse reads which messes up the 
## algorithms.
echo "[`date`]: Assigning taxonomy to ASVs with vsearch ..." >> $LOGFILE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime feature-classifier classify-consensus-vsearch \
    --verbose \
    --i-query /outputs/dada2_output/representative_sequences.qza \
    --i-reference-reads /data/silva-138-99-seqs.qza \
    --i-reference-taxonomy /data/silva-138-99-tax.qza \
    --output-dir /outputs/taxa \
    >> $LOGFILE

## VISUALIZE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime tools export \
    --input-path /outputs/taxa/classification.qza \
    --output-path /outputs/taxa \
    >> $LOGFILE
echo "[`date`]: Completed -- Assigned taxonomy to ASVs with vsearch ..." >> $LOGFILE

## GENERATE A TREE FOR PHYLOGENETIC DIVERSITY ANALYSIS
echo "[`date`]: Generating a tree for phylogenetic diversity analysis ..." >> $LOGFILE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime phylogeny align-to-tree-mafft-fasttree \
    --i-sequences /outputs/dada2_output/representative_sequences.qza \
    --o-alignment /outputs/aligned_reprepresentative_sequences.qza \
    --o-masked-alignment /outputs/masked_aligned_representative_sequences.qza \
    --o-tree /outputs/unrooted_tree.qza \
    --o-rooted-tree /outputs/rooted_tree.qza \
    >> $LOGFILE
echo "[`date`]: Completed -- Generating a tree for phylogenetic diversity analysis ..." >> $LOGFILE

## TAXA BARPLOTS
echo "[`date`]: Generating taxa barplots ..." >> $LOGFILE
singularity exec \
    -B $PROJECT_PATH/data:/data \
    -B $PROJECT_PATH/outputs/$RUNTIME:/outputs \
    $QIIME2_PATH \
    qiime taxa barplot \
    --i-table /outputs/dada2_output/table.qza \
    --i-taxonomy /outputs/taxa/classification.qza \
    --o-visualization /outputs/taxa-bar-plots.qzv \
    >> $LOGFILE
echo "[`date`]: Completed -- Generating taxa barplots ..." >> $LOGFILE
