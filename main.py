import streamlit as st
from website_checker.checker import check_website_performance, run_lighthouse, save_report, create_performance_dataframe
from pathlib import Path
import json


def categorize_score(score):
    if score >= 0.8:
        return 'Good', score
    elif score >= 0.4:
        return 'OK', score
    else:
        return 'Bad', score


def extract_lighthouse_summary(report):
    if 'error' in report:
        return {
            'error': report['error']
        }
    else:
        categories = report.get('categories', {})
        performance_score = categories.get('performance', {}).get('score', 0)
        accessibility_score = categories.get('accessibility', {}).get('score', 0)
        best_practices_score = categories.get('best-practices', {}).get('score', 0)
        seo_score = categories.get('seo', {}).get('score', 0)

        performance_category, performance_numeric = categorize_score(performance_score)
        accessibility_category, accessibility_numeric = categorize_score(accessibility_score)
        best_practices_category, best_practices_numeric = categorize_score(best_practices_score)
        seo_category, seo_numeric = categorize_score(seo_score)

        return {
            'performance': {
                'category': performance_category,
                'score': performance_numeric
            },
            'accessibility': {
                'category': accessibility_category,
                'score': accessibility_numeric
            },
            'best_practices': {
                'category': best_practices_category,
                'score': best_practices_numeric
            },
            'seo': {
                'category': seo_category,
                'score': seo_numeric
            }
        }


def main():
    st.title("Website Performance Checker")

    urls_input = st.text_area("Enter the URLs to check, separated by commas")
    if st.button("Check Performance"):
        urls = urls_input.split(',')
        urls = [url.strip() for url in urls] 

        st.write("Checking performance...")

        df_performance = create_performance_dataframe(urls)

        st.write("Performance Results:")
        st.dataframe(df_performance)

        lighthouse_results = []
        for url in urls:
            st.write(f"Running Web audit for {url}...")
            report = run_lighthouse(url)
            lighthouse_results.append(report)
            summary = extract_lighthouse_summary(report)
            if 'error' in summary:
                st.error(f"Error running Web audit for {url}. Make sure you are testing the correct URL and that the server is properly responding to all requests.")
            else:
                st.write(f"Performance Report for {url}:")
                st.write(f"Performance Score: {summary['performance']['category']} ({summary['performance']['score']})")
                st.write(f"Accessibility Score: {summary['accessibility']['category']} ({summary['accessibility']['score']})")
                st.write(f"Best Practices Score: {summary['best_practices']['category']} ({summary['best_practices']['score']})")
                st.write(f"SEO Score: {summary['seo']['category']} ({summary['seo']['score']})")
                st.success(f"Web audit for {url} completed successfully.")

    
        report_folder = Path('website_reports')
        report_folder.mkdir(exist_ok=True)
        
    
        report_file = report_folder / 'performance_report.txt'
        report_path = save_report(df_performance.to_dict(orient='records'), report_file)
        
   
        with open(report_path, 'r') as file:
            st.download_button(
                label="Download Performance Report",
                data=file,
                file_name="performance_report.txt",
                mime="text/plain"
            )

   
        lighthouse_report_file = report_folder / 'report.json'
        with open(lighthouse_report_file, 'w') as file:
            json.dump(lighthouse_results, file)

        with open(lighthouse_report_file, 'r') as file:
            st.download_button(
                label="Download Status Report",
                data=file,
                file_name="report.json",
                mime="application/json"
            )

if __name__ == '__main__':
    main()


