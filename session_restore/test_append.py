    def test_parse_file_empty_header_no_content(self, parser, tmp_path):
        """Test parsing file with header but no content after (line 101)."""
        log_file = tmp_path / "test.log"
        log_file.write_text('Script started on 2025-12-22 14:19:12 [COMMAND="test"]')
        
        result = parser.parse_file(log_file)
        assert result.header is not None
        assert len(result.content) == 0
