from external_libraries import *
from modules import *
import data_const as const

def get_spectral_centroid(audio_file: str, n_fft=2048*2) -> Tuple[np.ndarray, float, np.ndarray]:
    y, sr = librosa.load(audio_file, sr=None)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft)
    times = librosa.times_like(spectral_centroid, sr=sr)
    return spectral_centroid, sr, times

def calculate_section_averages(sections, feature_values, sr, times):
    section_averages = {'intro': [], 'drop': [], 'break': [], 'outro': []}
    feature_values = feature_values.flatten()

    for section in sections:
        label = section['label']
        start_index = np.argmax(times >= section['start'])
        end_index = np.argmax(times >= section['end'])
        if end_index == 0:
            end_index = len(feature_values)
        section_feature = feature_values[start_index:end_index]
        if len(section_feature) > 0:
            section_averages[label].append(section_feature.mean())

    section_averages_mean = {}
    for label, values in section_averages.items():
        if values:
            section_averages_mean[label] = np.mean(values)

    return section_averages_mean

def plot_bar_graph(section_averages):
    total_averages = {}
    for section, avgs in section_averages.items():
        if avgs:
            total_averages[section] = np.mean(avgs)

    plt.bar(total_averages.keys(), total_averages.values(), alpha=0.5, label='Average per section')
    for section, avgs in section_averages.items():
        if avgs:
            plt.scatter([section] * len(avgs), avgs, color='red', label='Individual averages' if section == 'intro' else "")

    plt.xlabel('Section')
    plt.ylabel('Average Spectral Centroid')
    plt.title('Average Spectral Centroid per Music Section')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_box_plot(section_averages):
    plt.boxplot(section_averages.values(), labels=section_averages.keys(), showmeans=True)
    plt.xlabel('Section')
    plt.ylabel('Average Spectral Centroid')
    plt.title('Box Plot of Average Spectral Centroid per Music Section')
    plt.tight_layout()
    plt.show()

def plot_violin_plot(section_averages):
    data_to_plot = [avgs for avgs in section_averages.values() if avgs]
    plt.violinplot(data_to_plot)
    plt.xticks(range(1, len(section_averages) + 1), section_averages.keys())
    plt.xlabel('Section')
    plt.ylabel('Average Spectral Centroid')
    plt.title('Violin Plot of Average Spectral Centroid per Music Section')
    plt.tight_layout()
    plt.show()

def process_file(json_path, song_directory, all_section_averages, allin1):
    section_data = allin1.load_section_data(json_path)

    filename = os.path.splitext(os.path.basename(json_path))[0] + '.mp3'
    file_path = os.path.join(song_directory, filename)
    spectral_centroid, sr, times = get_spectral_centroid(file_path)
    section_averages = calculate_section_averages(section_data['segments'], spectral_centroid, sr, times)

    for section, average in section_averages.items():
        all_section_averages[section].append(average)

def process_files(json_directory, song_directory, allin1, all_section_averages):
    for root, dirs, files in tqdm(os.walk(json_directory), desc="Processing files"):
        for file in tqdm(files, desc="Overall Progress", leave=False):
            if file.endswith(".json"):
                json_path = os.path.join(root, file)
                process_file(json_path, song_directory, all_section_averages, allin1)

def main(process_mode):
    song_directory = const.PROD_SONG_DIRECTORY
    json_directory = const.PROD_JSON_DIRECTORY
    allin1 = Allin1()
    all_section_averages = {'intro': [], 'drop': [], 'break': [], 'outro': []}

    process_files(json_directory, song_directory, allin1, all_section_averages)

    if process_mode == 'bar':
        plot_bar_graph(all_section_averages)
    elif process_mode == 'box':
        plot_box_plot(all_section_averages)
    elif process_mode == 'violin':
        plot_violin_plot(all_section_averages)

if __name__ == "__main__":
    process_mode = 'box'  # 'bar' | 'box' | 'violin'
    main(process_mode)
